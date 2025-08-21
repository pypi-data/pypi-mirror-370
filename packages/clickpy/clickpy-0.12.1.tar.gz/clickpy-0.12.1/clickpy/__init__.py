"""Clickpy, Automated mouse clicking scripts."""

import typer

from clickpy.exception import ClickStrategyNotFound
from clickpy.strategy import (
    CLICK_STRAEGIES,
    BasicClickStrategy,
    ClickStrategy,
    NaturalClickStrategy,
    StrategyEnum,
    generate_click_strategy,
)

__all__ = [
    "CLICK_STRAEGIES",
    "StrategyEnum",
    "BasicClickStrategy",
    "ClickStrategy",
    "NaturalClickStrategy",
    "generate_click_strategy",
]

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


def print_version(value: bool) -> None:
    if not value:
        return

    import importlib.metadata

    _DISTRIBUTION_METADATA = importlib.metadata.metadata("clickpy")

    print(f"clickpy: version {_DISTRIBUTION_METADATA['Version']}")
    raise typer.Exit(0)


def print_list(value: bool) -> None:
    if not value:
        return

        """Get simplified names of all strategies and print them to stdout."""
    typer.echo("\nAvailable click types:")
    for name in CLICK_STRAEGIES:
        typer.echo(name)
    typer.echo()  # extra newline
    raise typer.Exit(0)


# It's okay to use function calls here, because main should only be called once
# per exceution. But the values will be parsed of typer.Option will be parsed on
# the first pass.
@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", show_default=False),  # noqa
    fast: bool = typer.Option(False, "--fast", "-f", show_default=False),  # noqa
    version: bool = typer.Option(  # noqa
        False,
        "--version",
        "-v",
        show_default=False,
        callback=print_version,
        is_eager=True,
    ),
    list_clickers: bool = typer.Option(  # noqa
        False,
        "--list",
        "-l",
        help="Print a list of all available clicker types.",
        show_default=False,
        callback=print_list,
        is_eager=True,
    ),
    click_type: str = typer.Option(StrategyEnum.DEFAULT, "--type", "-t"),  # noqa
):
    """Clickpy, Automated mouse clicking with python."""
    message = "Running clickpy. Enter ctrl+c to stop.\n"
    if debug:
        message += f"\nUsing clicker type: {click_type}\n"
        message += f"""\nArgument list:
{debug=}
{fast=}
{list_clickers=}
{click_type=}
"""

    typer.echo(message)

    exit_code = 0
    try:
        click_strategy = generate_click_strategy(
            click_type=click_type, debug=debug, fast=fast
        )
        if debug:
            typer.echo(f"\nClick Strategy being used: {type(click_strategy)}\n")

        while True:
            click_strategy.click()

    except (ClickStrategyNotFound, TypeError):
        typer.echo(f"Argument {click_type!r} is not a valid clicker type.", err=True)
        exit_code = 1

    except KeyboardInterrupt:
        if debug:
            typer.echo("KeyboardInterrupt thrown and caught. Exiting script.")

    typer.echo("\n~~ Peace, out ~~")
    raise typer.Exit(code=exit_code)


def cli():  # pragma: no cover
    raise SystemExit(app())
