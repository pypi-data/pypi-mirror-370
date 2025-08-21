"""Project creation functionality."""

import shutil
from pathlib import Path
from typing import Dict, Any
import click
from jinja2 import Environment, FileSystemLoader

from ..utils.logging import get_logger


logger = get_logger("cli.create")


def create_server(name: str, template: str, output_dir: Path, extra_vars: Dict[str, Any] = None) -> None:
    """Create a new MCP server project from template."""
    project_path = output_dir / name
    
    if project_path.exists():
        click.echo(f"❌ Directory '{name}' already exists!")
        return
    
    # Validate template
    template_dir = get_template_dir(template)
    if not template_dir.exists():
        available = ", ".join(get_available_templates())
        click.echo(f"❌ Template '{template}' not found. Available: {available}")
        return
    
    click.echo(f"🚀 Creating MCP server '{name}' using '{template}' template...")
    
    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare template variables
        template_vars = {
            "project_name": name,
            "project_name_normalized": name.replace("-", "_").replace(" ", "_"),
            "template": template,
            "SERVICE_NAME": name,
            "SERVER_PORT": extra_vars.get("server_port", "8002") if extra_vars else "8002",
            "CONNECTOR_NAMES": extra_vars.get("connectors", ["encoder"]) if extra_vars else ["encoder"],
            "ACR_RESOURCE_GROUP": "your-resource-group",
            "AZURE_CONTAINER_REGISTRY": extra_vars.get("azure_registry", "your-registry") if extra_vars else "your-registry",
            "HELM_SERVICE_CONNECTION_NAME": "your-service-connection",
            "HELM_ACR_NAME": extra_vars.get("helm_registry", "your-helm-registry") if extra_vars else "your-helm-registry",
            "GITHUB_ENDPOINT": "your-github-endpoint",
            "GITHUB_REPO": "your-org/your-repo",
            "SONAR_SERVICE_CONNECTION": "your-sonar-connection",
            "SONAR_ORGANIZATION": "your-sonar-org"
        }
        
        # Add extra variables if provided
        if extra_vars:
            template_vars.update(extra_vars)
        
        # Copy and process template files
        copy_template_files(template_dir, project_path, template_vars)
        
        # Validate generated project
        validation_results = validate_generated_project(project_path, template_vars)
        
        if validation_results["success"]:
            click.echo(f"✅ Successfully created '{name}' MCP server!")
            if validation_results["warnings"]:
                click.echo("⚠️ Warnings:")
                for warning in validation_results["warnings"]:
                    click.echo(f"   {warning}")
        else:
            click.echo(f"❌ Project created but validation failed:")
            for error in validation_results["errors"]:
                click.echo(f"   {error}")
            click.echo("⚠️ Project may not work correctly. Please review the generated files.")
        click.echo("")
        click.echo("📋 Next steps:")
        click.echo(f"   cd {name}")
        click.echo("   # Option 1: Using Poetry")
        click.echo("   poetry install")
        click.echo("   poetry run python main.py")
        click.echo("")
        click.echo("   # Option 2: Using UV (recommended for production)")
        click.echo("   uv sync")
        click.echo("   uv run python main.py")
        click.echo("")
        click.echo("   # Common setup:")
        click.echo("   cp .env.example .env")
        click.echo("   # Add your connector configs to connectors/")
        click.echo("")
        click.echo("   # Build Docker image:")
        click.echo(f"   docker build -t {name} .")
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        click.echo(f"❌ Failed to create project: {e}")
        
        # Cleanup on failure
        if project_path.exists():
            shutil.rmtree(project_path)


def get_template_dir(template: str) -> Path:
    """Get the directory for a specific template."""
    templates_dir = Path(__file__).parent.parent / "templates"
    return templates_dir / template


def get_available_templates() -> list[str]:
    """Get list of available template names."""
    templates_dir = Path(__file__).parent.parent / "templates"
    if not templates_dir.exists():
        return []
    
    templates = []
    for item in templates_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            templates.append(item.name)
    
    return sorted(templates)


def validate_generated_project(project_path: Path, template_vars: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the generated project for common issues."""
    errors = []
    warnings = []
    
    # Check required files exist
    required_files = ["main.py", "pyproject.toml", "README.md"]
    for file_name in required_files:
        file_path = project_path / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
        else:
            # Check for unprocessed Jinja2 variables
            content = file_path.read_text()
            if "{{" in content or "}}" in content:
                errors.append(f"Unprocessed Jinja2 variables found in: {file_name}")
            
            # Check for expected content
            if file_name == "main.py":
                if "GenesisMCPServer" not in content:
                    errors.append("main.py missing GenesisMCPServer import")
                if template_vars["project_name_normalized"] not in content:
                    warnings.append(f"main.py may not contain expected project name: {template_vars['project_name_normalized']}")
            
            elif file_name == "pyproject.toml":
                if "genesis-mcp-core" not in content:
                    errors.append("pyproject.toml missing genesis-mcp-core dependency")
                if template_vars["project_name"] not in content:
                    errors.append(f"pyproject.toml missing project name: {template_vars['project_name']}")
    
    # Check connectors directory
    connectors_dir = project_path / "connectors"
    if not connectors_dir.exists():
        errors.append("Missing connectors directory")
    elif not (connectors_dir / "README.md").exists():
        warnings.append("Missing connectors/README.md")
    
    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def copy_template_files(template_dir: Path, project_path: Path, template_vars: Dict[str, Any]) -> None:
    """Copy and process template files to the project directory."""
    # Set up Jinja2 environment
    jinja_env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True
    )
    
    # Walk through all files in template directory
    for template_file in template_dir.rglob("*"):
        if template_file.is_file():
            # Calculate relative path
            rel_path = template_file.relative_to(template_dir)
            
            # Process path template variables (e.g., {{ SERVICE_NAME }})
            target_rel_path_str = str(rel_path)
            for var_name, var_value in template_vars.items():
                target_rel_path_str = target_rel_path_str.replace(f"{{{{ {var_name} }}}}", str(var_value))
            
            target_path = project_path / target_rel_path_str
            
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Process file based on extension or name pattern
            should_process = (
                template_file.suffix in [".py", ".toml", ".md", ".txt", ".env", ".json", ".yaml", ".yml", ".tpl", ".lock"] or
                template_file.name.startswith("env.") or
                template_file.name in ["Dockerfile", "Makefile", ".gitignore", "Chart.yaml", "values.yaml", "NOTES.txt", "uv.lock"]
            )
            
            if should_process:
                # Process as Jinja2 template
                try:
                    template = jinja_env.get_template(str(rel_path))
                    content = template.render(**template_vars)
                    target_path.write_text(content, encoding="utf-8")
                    logger.info(f"✅ Processed template: {rel_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to process template {rel_path}: {e}")
                    # Fall back to manual variable replacement for Helm templates
                    try:
                        content = template_file.read_text(encoding="utf-8")
                        # Replace SERVICE_NAME variable manually
                        content = content.replace("{{ SERVICE_NAME }}", template_vars["SERVICE_NAME"])
                        # Replace other common variables that might appear in Helm templates
                        for var_name, var_value in template_vars.items():
                            if var_name != "SERVICE_NAME":  # Already handled above
                                content = content.replace(f"{{{{ {var_name} }}}}", str(var_value))
                        target_path.write_text(content, encoding="utf-8")
                        logger.info(f"✅ Manually processed variables in: {rel_path}")
                    except Exception as fallback_error:
                        logger.error(f"❌ Manual processing also failed for {rel_path}: {fallback_error}")
                        # Final fallback to direct copy
                        shutil.copy2(template_file, target_path)
                        logger.warning(f"⚠️ Final fallback: Copied {rel_path} without processing")
            else:
                # Copy binary files directly
                shutil.copy2(template_file, target_path)