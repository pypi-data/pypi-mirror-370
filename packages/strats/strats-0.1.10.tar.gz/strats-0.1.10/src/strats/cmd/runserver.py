import typer
import uvicorn

app = typer.Typer(no_args_is_help=True)


@app.command()
def runserver(
    target: str = typer.Option("main:app", "--target"),
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
    access_log: bool = False,
    factory: bool = typer.Option(
        False,
        "--factory",
        help="Treat target as an application factory, not an ASGI app instance",
    ),
):
    """Run development server (default: main:app)."""
    # target をそのまま uvicorn.run に渡す
    uvicorn.run(
        target,
        host=host,
        port=port,
        reload=reload,
        access_log=access_log,
        log_config=None,
        factory=factory,
    )
