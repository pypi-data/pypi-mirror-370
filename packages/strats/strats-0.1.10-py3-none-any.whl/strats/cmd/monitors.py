from urllib.parse import urljoin

import httpx
import typer

from .common import DEFAULT_URL

app = typer.Typer(no_args_is_help=True)


@app.command()
def show():
    url = urljoin(DEFAULT_URL, "/monitors")
    res = httpx.get(url)
    show_status(res)


@app.command()
def start():
    url = urljoin(DEFAULT_URL, "/monitors/start")
    res = httpx.post(url)
    show_status(res)


@app.command()
def stop():
    url = urljoin(DEFAULT_URL, "/monitors/stop")
    res = httpx.post(url)
    show_status(res)


def show_status(res):
    if res.status_code != 200:
        typer.echo(f"API reqeust failed: {res.text}", err=True)
        raise typer.Exit()

    data = res.json()

    if not data["is_configured"]:
        print("monitor is not configured")
        return

    for name, monitor in data["monitors"].items():
        status = "RUNNING" if monitor["is_running"] else "STOPPED"
        print(f"{name}: {status}")
