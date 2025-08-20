from urllib.parse import urljoin

import httpx
import typer

from .common import DEFAULT_URL

app = typer.Typer(no_args_is_help=True)


@app.command()
def show():
    url = urljoin(DEFAULT_URL, "/clock")
    res = httpx.get(url)
    show_status(res)


@app.command()
def start():
    url = urljoin(DEFAULT_URL, "/clock/start")
    res = httpx.post(url)
    show_status(res)


@app.command()
def stop():
    url = urljoin(DEFAULT_URL, "/clock/stop")
    res = httpx.post(url)
    show_status(res)


def show_status(res):
    if res.status_code != 200:
        typer.echo(f"API reqeust failed: {res.text}", err=True)
        raise typer.Exit()

    data = res.json()

    print(f"current: {data['datetime']}")
    print(f"is_real: {data['is_real']}")
    if not data["is_real"]:
        print(f"is_running: {data['is_running']}")
