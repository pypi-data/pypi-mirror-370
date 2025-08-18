"""Main CLI entry point for Genesis MCP Core."""

import click
from pathlib import Path
from typing import Optional

from .create import create_server
from .templates import list_templates


@click.group()
@click.version_option(version="0.1.0", prog_name="genesis-mcp")
def cli():
    """Genesis MCP Core - Build powerful MCP servers with ease."""
    pass


@cli.command()
@click.argument("name")
@click.option(
    "--template", 
    "-t", 
    default="basic",
    help="Template to use (basic, healthcare, api, database)"
)
@click.option(
    "--output-dir",
    "-o", 
    type=click.Path(),
    help="Output directory (defaults to current directory)"
)
@click.option(
    "--server-port",
    "-p",
    default="8000",
    help="Server port number (default: 8000)"
)
@click.option(
    "--connectors",
    "-c",
    multiple=True,
    help="Connectors to include (can be specified multiple times)"
)
@click.option(
    "--azure-registry",
    help="Azure Container Registry name"
)
@click.option(
    "--helm-registry",
    help="Helm registry name"
)
def create(name: str, template: str, output_dir: Optional[str], server_port: str, 
          connectors: tuple, azure_registry: Optional[str], helm_registry: Optional[str]):
    """Create a new MCP server project."""
    output_path = Path(output_dir) if output_dir else Path.cwd()
    
    # Prepare additional template variables
    extra_vars = {
        "server_port": server_port,
        "connectors": list(connectors) if connectors else ["encoder"],
        "azure_registry": azure_registry or "your-registry",
        "helm_registry": helm_registry or "your-helm-registry"
    }
    
    create_server(name, template, output_path, extra_vars)


@cli.group()
def templates():
    """Manage project templates."""
    pass


@templates.command("list")
def templates_list():
    """List available project templates."""
    list_templates()


if __name__ == "__main__":
    cli()