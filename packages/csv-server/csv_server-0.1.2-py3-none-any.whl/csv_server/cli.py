"""Command line interface for csv-server."""

import click
from pathlib import Path
from .version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="csv-server")
def main():
    """CSV Server - REST API for CSV files.
    
    Transform your CSV files into a REST API with automatic schema inference,
    data validation, and configurable access control.
    """
    pass


@main.command()
@click.argument('data_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--readonly', is_flag=True, help='Enable readonly mode (only GET requests)')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to YAML config file')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def serve(data_dir, host, port, readonly, config, reload):
    """Serve CSV files as REST API.
    
    Examples:
    
        csv-server serve ./data
        csv-server serve ./data --config config.yaml
        csv-server serve ./data --readonly
        csv-server serve ./data --reload
    """
    try:
        # Import here to avoid circular imports
        from . import serve_csv_directory
        
        serve_csv_directory(
            data_dir=data_dir,
            host=host,
            port=port,
            readonly=readonly,
            config_file=config,
            auto_reload=reload
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('data_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', type=click.Path(), help='Output config file path')
@click.option('--readonly', is_flag=True, help='Set discovered resources as readonly')
def discover(data_dir, output, readonly):
    """Discover CSV files and generate configuration.
    
    Examples:
    
        csv-server discover ./data
        csv-server discover ./data --output config.yaml
        csv-server discover ./data --readonly
    """
    try:
        from .config import discover_csv_files, save_config
        import yaml
        
        data_path = Path(data_dir)
        config = discover_csv_files(data_path, readonly=readonly)
        
        if not config["resources"]:
            click.echo("No CSV files found in the specified directory.", err=True)
            return
        
        config_yaml = yaml.dump(config, default_flow_style=False, indent=2)
        
        if output:
            save_config(config, output)
            click.echo(f"Configuration saved to {output}")
        else:
            click.echo("# Generated CSV Server configuration")
            click.echo(config_yaml)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()