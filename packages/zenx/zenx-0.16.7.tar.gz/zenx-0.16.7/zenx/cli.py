from typing import Annotated, List
import pathlib
import typer

from zenx.discovery import discover_local_module
from zenx.engine import Engine
from zenx.listeners import Listener
from zenx.spiders import Spider


app = typer.Typer()


@app.callback()
def callback():
    discover_local_module("spiders")
    discover_local_module("listeners")


@app.command()
def list():
    spiders_available = Spider.spider_list()
    listeners_available = Listener.listener_list()
    typer.secho("Available spiders:", fg=typer.colors.GREEN, bold=True)
    for spider in spiders_available:
        typer.echo(f"- {spider}")
    typer.secho("Available listeners:", fg=typer.colors.GREEN, bold=True)
    for listener in listeners_available:
        typer.echo(f"- {listener}")


@app.command()
def crawl(spiders: List[str], forever: Annotated[bool, typer.Option(help="Run spiders continuously")] = False):
    spiders_available = Spider.spider_list()
    engine = Engine(forever=forever)
    if not spiders_available:
        typer.secho("❌ No spiders found to run.", fg=typer.colors.RED)
        raise typer.Exit()
    
    if len(spiders) > 1:
        for spider in spiders:
            if spider not in spiders_available:
                typer.secho(f"❌ Spider '{spider}' not found. Check available spiders with the 'list' command.", fg=typer.colors.RED)
                raise typer.Exit()
        typer.secho(f"🚀 Starting spiders: {', '.join(spiders)}", fg=typer.colors.CYAN)
        engine.run_spiders(spiders)
    
    elif spiders[0] == "all":
        typer.secho(f"🚀 Starting spiders: {', '.join(spiders_available)}", fg=typer.colors.CYAN)
        engine.run_spiders(spiders_available)
    
    else:
        spider = spiders[0]
        if spider not in spiders_available:
            typer.secho(f"❌ Spider '{spider}' not found. Check available spiders with the 'list' command.", fg=typer.colors.RED)
            raise typer.Exit()
        typer.secho(f"🚀 Starting spider: {spider}", fg=typer.colors.CYAN)
        engine.run_spider(spider)


@app.command()
def listen(listener: str):
    listeners_available = Listener.listener_list()
    engine = Engine(forever=False)
    if not listeners_available :
        typer.secho("❌ No listeners found to run.", fg=typer.colors.RED)
        raise typer.Exit()
    typer.secho(f"🚀 Starting listener: {listener}", fg=typer.colors.CYAN)
    engine.run_listener(listener)


@app.command()
def startproject(project_name: str):
    # e.g project_root/
    # /project_root/{project_name}
    project_path = pathlib.Path(project_name)
    # /project_root/{project_name}/spiders
    spiders_path = project_path / "spiders"
    # /project_root/{project_name}/listeners
    listeners_path = project_path / "listeners"
    # /project_root/zenx.toml
    config_path = project_path.parent / "zenx.toml"

    if project_path.exists():
        typer.secho(f"❌ Project '{project_name}' already exists in this directory.", fg=typer.colors.RED)
        raise typer.Exit()
    try:
        spiders_path.mkdir(parents=True, exist_ok=True)
        (spiders_path / "__init__.py").touch()
        listeners_path.mkdir(parents=True, exist_ok=True)
        (listeners_path / "__init__.py").touch()
        config_path.write_text(f'project = "{project_name}"\n')

        typer.secho(f"✅ Project '{project_name}' created successfully.", fg=typer.colors.GREEN)
    except OSError as e:
        typer.secho(f"❌ Error creating project: {e}", fg=typer.colors.RED)
        raise typer.Exit()

