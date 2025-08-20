"""Configuration management for csv-server."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigurationError


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If config file cannot be loaded or is invalid
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate basic structure
        if not isinstance(config, dict):
            raise ConfigurationError("Config must be a dictionary")
        
        if "resources" not in config:
            config["resources"] = {}
        
        return config
        
    except FileNotFoundError:
        raise ConfigurationError(f"Config file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading config: {e}")


def discover_csv_files(data_dir: Path, readonly: bool = False) -> Dict[str, Any]:
    """Auto-discover CSV files and generate configuration.
    
    Args:
        data_dir: Directory to scan for CSV files
        readonly: Default readonly setting for discovered resources
        
    Returns:
        Configuration dictionary with discovered resources
    """
    config = {"resources": {}}
    
    if not data_dir.exists():
        return config
    
    for csv_file in data_dir.glob("*.csv"):
        name = csv_file.stem
        config["resources"][name] = {
            "file": csv_file.name,
            "primary_key": "id",
            "readonly": readonly
        }
    
    return config


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration
        
    Raises:
        ConfigurationError: If config cannot be saved
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    except Exception as e:
        raise ConfigurationError(f"Error saving config: {e}")


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ConfigurationError("Configuration must be a dictionary")
    
    if "resources" not in config:
        raise ConfigurationError("Configuration must have 'resources' section")
    
    resources = config["resources"]
    if not isinstance(resources, dict):
        raise ConfigurationError("'resources' must be a dictionary")
    
    for name, resource_config in resources.items():
        if not isinstance(resource_config, dict):
            raise ConfigurationError(f"Resource '{name}' config must be a dictionary")
        
        if "file" not in resource_config:
            raise ConfigurationError(f"Resource '{name}' must specify 'file'")
        
        # Validate optional fields
        if "primary_key" in resource_config and not isinstance(resource_config["primary_key"], str):
            raise ConfigurationError(f"Resource '{name}' primary_key must be a string")
        
        if "readonly" in resource_config and not isinstance(resource_config["readonly"], bool):
            raise ConfigurationError(f"Resource '{name}' readonly must be a boolean")