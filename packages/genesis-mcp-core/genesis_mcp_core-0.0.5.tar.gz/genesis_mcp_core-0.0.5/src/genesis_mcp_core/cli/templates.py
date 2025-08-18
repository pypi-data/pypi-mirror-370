"""Template management functionality."""

import click
from pathlib import Path
from ..utils.logging import get_logger


logger = get_logger("cli.templates")


def list_templates() -> None:
    """List all available project templates."""
    templates_dir = Path(__file__).parent.parent / "templates"
    
    if not templates_dir.exists():
        click.echo("❌ No templates directory found!")
        return
    
    templates = []
    for item in templates_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Try to read description from template info
            info_file = item / "template.info"
            description = "No description available"
            
            if info_file.exists():
                try:
                    description = info_file.read_text().strip()
                except Exception:
                    pass
            
            templates.append((item.name, description))
    
    if not templates:
        click.echo("❌ No templates found!")
        return
    
    click.echo("📋 Available templates:")
    click.echo("")
    
    for name, description in sorted(templates):
        click.echo(f"  🔧 {name:<12} - {description}")
    
    click.echo("")
    click.echo("💡 Use: genesis-mcp create <project-name> --template=<template-name>")