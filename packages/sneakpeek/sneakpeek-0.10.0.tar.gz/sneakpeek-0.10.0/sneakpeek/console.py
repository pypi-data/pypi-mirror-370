# third-party imprts
import json

import click
import uvicorn
from loguru import logger
from rich import print

# app imports
from sneakpeek.server import get_link_preview


@click.group()
def cli():
    pass


@click.command()
@click.option("--host", default="localhost", help="Sever Host.")
@click.option("--port", default=9000, help="Server Port.")
@click.option("--reload", is_flag=True, help="Enable auto-reload on code change.")
@click.option("--workers", default=2, help="No. of worker threads.")
def serve(host, port, reload, workers):
    """Spin up a simple server using FastAPI."""
    logger.info(
        f"Starting a server on {host}:{port} "
        f"with auto reload {reload} and {workers} workers"
    )
    uvicorn.run(
        "sneakpeek.server:app", host=host, port=port, reload=reload, workers=workers
    )


@click.command()
@click.option("--url", required=True, help="URL to be generate a link preview for.")
@click.option(
    "--scrape",
    is_flag=True,
    help="Try scraping website if open graph tags are not present.",
)
def preview(url, scrape):
    """Link preview the command line."""
    print(json.dumps(get_link_preview(url=url, scrape=scrape), indent=4))


cli.add_command(serve)
cli.add_command(preview)
