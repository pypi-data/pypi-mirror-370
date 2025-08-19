import os, sys
import click
import shutil
from pathlib import Path
from slush.server import run
from importlib import import_module
from importlib.metadata import version, PackageNotFoundError

sys.path.insert(0, os.getcwd())


def get_version():
    try:
        return version("slush")
    except PackageNotFoundError:
        return "unknown"
    
@click.group()
@click.version_option(get_version(), "-v", "--version", message="Slush version: %(version)s")
@click.help_option("--help", "-h")
def cli():
    """🧊 Slush CLI"""
    pass

@cli.command()
@click.argument('app_path')
@click.option('--host', default='127.0.0.1', help='Host to bind the server to')
@click.option('--port', default=8000, type=int, help='Port to run the server on')
@click.option('--reload', default=True, is_flag=True, help='Enable auto-reloading of the server')
def runserver(app_path, host, port, reload):
    """Start your Slush app (example: slush runserver example:app)"""
    if ":" not in app_path:
        raise click.UsageError("⚠️ Please provide app in format module:app (e.g. example:app)")

    module_name, app_name = app_path.split(":")
    try:
        mod = import_module(module_name)
        app = getattr(mod, app_name)
    except (ImportError, AttributeError) as e:
        raise click.ClickException(f"❌ Failed to import app: {e}")

    click.secho(f"🧊 Starting Slush app [{module_name}.{app_name}] at http://{host}:{port}", fg='green')
    run(app, host=host, port=port, reload=reload)


@cli.command("create-project")
def create_project():
    """
    Copy the Slush boilerplate files into the CURRENT working directory.
    Usage:
        mkdir myAPI && cd myAPI
        slush create-project
    """
    boilerplate_dir = Path(__file__).resolve().parent.parent / "boilerplate"
    target_dir = Path.cwd()

    if not boilerplate_dir.exists():
        raise click.ClickException("❌ Boilerplate folder not found in package.")

    for item in boilerplate_dir.iterdir():
        target_path = target_dir / item.name

        if target_path.exists():
            click.secho(f"⚠️ Skipping (already exists): {target_path}", fg="yellow")
            continue

        if item.is_dir():
            shutil.copytree(item, target_path)
        else:
            shutil.copy2(item, target_path)

        click.secho(f"✅ Created: {target_path}", fg="green")

    click.secho("\n🎉 Boilerplate copied successfully!", fg="cyan")
    click.secho("Next steps:", fg="yellow")
    click.echo("  - Edit files as needed")
    click.echo("  - Run: slush runserver main:app")