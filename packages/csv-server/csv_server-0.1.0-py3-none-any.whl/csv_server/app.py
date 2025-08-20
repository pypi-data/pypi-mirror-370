# FastAPI app factory.
# For each CSV in dir, create routes.
# Respect readonly: POST/PUT/PATCH/DELETE -> 405.
# Add CORS and exception handlers.

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Dict, Any, List
from csv_server.storage.csv_store import CSVStorage
import os
import csv

def infer_column_types(file_path: Path) -> Dict[str, str]:
    """Infer data types for each column by sampling the data."""
    if not file_path.exists():
        return {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    if not rows:
        return {}
    
    schema = {}
    for column in rows[0].keys():
        # Sample values from this column (skip empty values)
        values = [row[column] for row in rows[:10] if row[column].strip()]
        
        if not values:
            schema[column] = "string"
            continue
            
        # Try to infer type
        all_int = True
        all_float = True
        
        for value in values:
            try:
                int(value)
            except ValueError:
                all_int = False
            
            try:
                float(value)
            except ValueError:
                all_float = False
        
        if all_int:
            schema[column] = "integer"
        elif all_float:
            schema[column] = "float"
        else:
            schema[column] = "string"
    
    return schema

def validate_data(payload: Dict[str, Any], schema: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate and convert payload data according to schema.
    
    Args:
        payload: The data to validate
        schema: The expected schema (column -> type mapping)
    
    Returns:
        Validated and converted payload
    
    Raises:
        HTTPException: If validation fails
    """
    validated_payload = {}
    errors = []
    
    for field, value in payload.items():
        # Skip validation for fields not in schema (new columns are allowed)
        if field not in schema:
            validated_payload[field] = str(value)  # Default to string for new fields
            continue
        
        expected_type = schema[field]
        
        # Handle None/empty values
        if value is None or value == "":
            validated_payload[field] = ""
            continue
        
        # Convert and validate based on expected type
        try:
            if expected_type == "integer":
                if isinstance(value, str) and value.strip() == "":
                    validated_payload[field] = ""
                else:
                    validated_payload[field] = str(int(value))
            
            elif expected_type == "float":
                if isinstance(value, str) and value.strip() == "":
                    validated_payload[field] = ""
                else:
                    validated_payload[field] = str(float(value))
            
            elif expected_type == "string":
                validated_payload[field] = str(value)
            
            else:
                # Unknown type, default to string
                validated_payload[field] = str(value)
                
        except (ValueError, TypeError) as e:
            errors.append(f"Field '{field}': Expected {expected_type}, got '{value}' ({type(value).__name__})")
    
    if errors:
        raise HTTPException(
            status_code=422, 
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )
    
    return validated_payload

def get_required_fields(schema: Dict[str, str], existing_data: List[Dict[str, Any]] = None) -> List[str]:
    """
    Determine which fields are required based on existing data.
    For now, we'll consider the primary key as required for updates.
    """
    # This could be enhanced to check which fields are never empty in existing data
    return []

def create_app(data_dir: Path, readonly: bool = True, config: dict = None) -> FastAPI:
    app = FastAPI(title="CSV Server", docs_url="/docs")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if config is None:
        config = {"resources": {}}

    # Store config and data_dir in app state for the universal schema endpoint
    app.state.config = config
    app.state.data_dir = data_dir

    # Universal schema endpoint
    @app.get("/{resource_name}/schema", tags=["Schema"])
    async def get_schema(resource_name: str):
        """Get schema for any resource by extracting resource name from URL."""
        print(f"DEBUG: Schema endpoint called for resource: {resource_name}")
        
        # Check if resource exists in config
        if resource_name not in app.state.config.get("resources", {}):
            raise HTTPException(status_code=404, detail=f"Resource '{resource_name}' not found")
        
        # Get file path for this resource
        resource_cfg = app.state.config["resources"][resource_name]
        file_path = app.state.data_dir / resource_cfg["file"]
        
        # Generate schema on-the-fly
        schema = infer_column_types(file_path)
        print(f"DEBUG: Generated schema for {resource_name}: {schema}")
        
        return {"schema": schema}

    # Define RouteHandlers class
    class RouteHandlers:
        def __init__(self, storage_instance, resource_name):
            self.storage = storage_instance
            self.resource_name = resource_name
            self._schema_cache = None

        def get_schema(self) -> Dict[str, str]:
            """Get cached schema or compute it."""
            if self._schema_cache is None:
                self._schema_cache = infer_column_types(self.storage.path)
            return self._schema_cache

        def invalidate_schema_cache(self):
            """Invalidate schema cache when data structure changes."""
            self._schema_cache = None

        async def list_rows(self, limit: int = 50, offset: int = 0):
            rows = self.storage.list(limit=limit, offset=offset)
            return {"items": rows, "total": len(self.storage.list(10000, 0))}

        async def get_row(self, item_id: str):
            row = self.storage.get(item_id)
            if not row:
                raise HTTPException(status_code=404, detail="Not found")
            return row

        async def create_row(self, payload: Dict[str, Any]):
            print(f"DEBUG: Creating row with payload: {payload}")
            
            # Get schema and validate data
            schema = self.get_schema()
            print(f"DEBUG: Using schema for validation: {schema}")
            
            try:
                validated_payload = validate_data(payload, schema)
                print(f"DEBUG: Validated payload: {validated_payload}")
                
                # Create the row
                result = self.storage.create(validated_payload)
                
                # Invalidate schema cache in case new columns were added
                self.invalidate_schema_cache()
                
                return result
                
            except HTTPException:
                raise  # Re-raise validation errors
            except Exception as e:
                print(f"DEBUG: Error creating row: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create row: {str(e)}")

        async def update_row(self, item_id: str, payload: Dict[str, Any]):
            print(f"DEBUG: Updating row {item_id} with payload: {payload}")
            
            # Get schema and validate data
            schema = self.get_schema()
            print(f"DEBUG: Using schema for validation: {schema}")
            
            try:
                validated_payload = validate_data(payload, schema)
                print(f"DEBUG: Validated payload: {validated_payload}")
                
                # Update the row
                result = self.storage.update(item_id, validated_payload)
                
                # Invalidate schema cache in case new columns were added
                self.invalidate_schema_cache()
                
                return result
                
            except KeyError:
                raise HTTPException(status_code=404, detail="Not found")
            except HTTPException:
                raise  # Re-raise validation errors
            except Exception as e:
                print(f"DEBUG: Error updating row: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to update row: {str(e)}")

        async def delete_row(self, item_id: str):
            self.storage.delete(item_id)
            return JSONResponse(status_code=204, content={})

    # Create routes for each resource (excluding schema - handled by universal endpoint)
    for name, resource_cfg in config.get("resources", {}).items():
        print(f"DEBUG: Processing resource: {name}")
        file = data_dir / resource_cfg["file"]
        pk = resource_cfg.get("primary_key", "id")
        res_readonly = resource_cfg.get("readonly", readonly)
        storage = CSVStorage(file, pk=pk)
        
        route_prefix = f"/{name}"
        print(f"DEBUG: Registering routes with prefix: {route_prefix}")

        # Create handlers instance
        handlers = RouteHandlers(storage, name)

        app.get(route_prefix, tags=[name])(handlers.list_rows)
        app.get(f"{route_prefix}/{{item_id}}", tags=[name])(handlers.get_row)

        if not res_readonly:
            app.post(route_prefix, status_code=201, tags=[name])(handlers.create_row)
            app.put(f"{route_prefix}/{{item_id}}", tags=[name])(handlers.update_row)
            app.delete(f"{route_prefix}/{{item_id}}", status_code=204, tags=[name])(handlers.delete_row)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        print(f"DEBUG: Exception caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    return app