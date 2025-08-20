import typer

from strats import __version__

from .clock import app as clock_app
from .monitors import app as monitors_app
from .runserver import app as runserver_app
from .strategy import app as strategy_app

app = typer.Typer(
    rich_markup_mode=None,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(strategy_app, name="strategy")
app.add_typer(monitors_app, name="monitors")
app.add_typer(clock_app, name="clock")
app.add_typer(runserver_app)


@app.command()
def version():
    print(f"strats version: {__version__}")


if __name__ == "__main__":
    app()
