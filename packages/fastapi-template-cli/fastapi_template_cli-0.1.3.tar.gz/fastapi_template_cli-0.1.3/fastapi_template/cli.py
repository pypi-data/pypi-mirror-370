"""CLI interface for fastapi-template-cli."""

import os
import shutil
from pathlib import Path
import click


class TemplateError(Exception):
    """Exception raised for template-related errors."""
    pass


def get_template_path(template_name: str) -> Path:
    """Get the absolute path to a template directory."""
    package_dir = Path(__file__).parent
    template_path = package_dir / "templates" / template_name
    
    if not template_path.exists():
        raise TemplateError(f"Template '{template_name}' not found at {template_path}")
    
    return template_path


def copy_template(template_path: Path, target_path: Path) -> None:
    """Copy template directory to target location."""
    try:
        shutil.copytree(template_path, target_path)
    except Exception as e:
        raise TemplateError(f"Failed to copy template: {e}")


def print_next_steps(project_name: str, template_type: str) -> None:
    """Print instructions for getting started with the new project."""
    click.echo("\n🎉 Project created successfully!")
    click.echo(f"\n📁 Your new FastAPI project is ready: {project_name}")
    
    if template_type in ["api_only", "fullstack"]:
        click.echo("\n📋 Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  pip install -r requirements.txt")
        click.echo("  uvicorn app.main:app --reload")
    else:
        click.echo("\n📋 Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  pip install fastapi uvicorn[standard]")
        click.echo("  uvicorn main:app --reload")


@click.group()
def cli() -> None:
    """FastAPI Template CLI - Scaffold modern FastAPI projects."""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["minimal", "api_only", "fullstack"]),
    help="Project template type (bypasses interactive selection)",
)
def new(project_name: str, template: str = None) -> None:
    """Create a new FastAPI project with the specified template."""
    target_path = Path.cwd() / project_name
    
    if target_path.exists():
        click.echo(f"❌ Directory '{project_name}' already exists.", err=True)
        raise click.Abort()
    
    # Interactive template selection if not provided
    if template is None:
        click.echo("🚀 Welcome to FastAPI Template CLI!")
        click.echo("\nPlease select a project type:")
        click.echo("  1) Minimal - Basic FastAPI app with Hello World")
        click.echo("  2) API Only - Modular structure for medium projects")
        click.echo("  3) Full-stack - Production-ready with database & auth")
        
        choice = click.prompt(
            "Enter your choice (1-3)",
            type=click.IntRange(1, 3),
            default=2
        )
        
        template_map = {1: "minimal", 2: "api_only", 3: "fullstack"}
        template = template_map[choice]
    
    try:
        template_path = get_template_path(template)
        
        click.echo(f"📦 Creating {template} project: {project_name}")
        
        copy_template(template_path, target_path)
        print_next_steps(project_name, template)
        
    except TemplateError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        raise click.Abort()


@cli.command()
def templates() -> None:
    """List available project templates."""
    click.echo("📋 Available templates:")
    click.echo("  • minimal - Basic FastAPI app")
    click.echo("  • api_only - Modular structure with routers and models")
    click.echo("  • fullstack - Production-ready with database, auth, and Docker")


if __name__ == "__main__":
    cli()