import asyncio
import importlib.util
import pathlib
import sys
from typing import Optional

import rich
import typer

from fastcrawl.core import FastCrawl

cli = typer.Typer(name="FastCrawl", help="FastCrawl CLI for running crawlers.", add_completion=False)


@cli.command("list", help="List of available crawlers in FastCrawl application.")
def list_crawlers(
    path: pathlib.Path = typer.Argument(
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to python file containing the FastCrawl application.",
    ),
    app_var: str = typer.Option(
        default="app",
        help="Name of the FastCrawl application variable in the python file. Default is 'app'.",
    ),
) -> None:
    """Shows the list of available crawlers in the FastCrawl application defined in the specified python file.

    Args:
        path (pathlib.Path): Path to the python file containing the FastCrawl application.
        app_var (str): Name of the FastCrawl application variable in the python file. Default is 'app'.

    """
    fastcrawl_app = import_app_from_module(path, app_var)

    crawlers_len = len(fastcrawl_app.crawlers)
    rich.print(
        f"Found {crawlers_len} crawler{'s' if crawlers_len > 1 else ''} "
        f"in application [bold green]{fastcrawl_app.name}[/bold green]"
    )
    for name in fastcrawl_app.crawlers:
        if name == fastcrawl_app.name:
            rich.print(f"- [bold blue]{name}[/bold blue] (default)")
        else:
            rich.print(f"- [bold blue]{name}[/bold blue]")


@cli.command("run", help="Run the FastCrawl application.")
def run_crawler(
    path: pathlib.Path = typer.Argument(
        exists=True,
        dir_okay=False,
        resolve_path=True,
        help="Path to python file containing the FastCrawl application.",
    ),
    app_var: str = typer.Option(
        default="app",
        help="Name of the FastCrawl application variable in the python file. Default is 'app'.",
    ),
    crawler_name: Optional[str] = typer.Option(
        default=None,
        help=(
            "Name of the crawler to run. "
            "Provide it if you want to run only specific crawler from the application. "
            "If not provided, all crawlers will be run."
        ),
    ),
) -> None:
    """Runs the FastCrawl application defined in the specified python file.

    Args:
        path (pathlib.Path): Path to the python file containing the FastCrawl application.
        app_var (str): Name of the FastCrawl application variable in the python file. Default is 'app'.
        crawler_name (Optional[str]): Name of the crawler to run. Default is None.

    """
    fastcrawl_app = import_app_from_module(path, app_var)

    if crawler_name:
        rich.print(
            f"Running crawler [bold blue]{crawler_name}[/bold blue] from app [bold green]{fastcrawl_app.name}[/bold green]"
        )
    else:
        rich.print(f"Running app [bold green]{fastcrawl_app.name}[/bold green]")
    asyncio.run(fastcrawl_app.run(crawler_name))


def import_app_from_module(path: pathlib.Path, app_var: str) -> FastCrawl:
    """Returns imported FastCrawl application from a python file.

    Args:
        path (pathlib.Path): Path to the python file containing the FastCrawl application.
        app_var (str): Name of the FastCrawl application variable in the python file.

    Raises:
        ValueError: If the provided path is not a python file.
        ImportError: If the module cannot be loaded.
        AttributeError: If the module does not have the specified application variable.
        TypeError: If the specified application is not an instance of FastCrawl.

    """
    if path.suffix != ".py":
        raise ValueError(f"File '{path}' is not a python file. Please provide a valid python file.")
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load '{path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, app_var):
        raise AttributeError(f"Module '{module_name}' does not have attribute '{app_var}'")
    fastcrawl_app = getattr(module, app_var)
    if not isinstance(fastcrawl_app, FastCrawl):
        raise TypeError(f"Attribute '{app_var}' in module '{module_name}' is not an instance of FastCrawl")
    return fastcrawl_app


if __name__ == "__main__":
    cli()
