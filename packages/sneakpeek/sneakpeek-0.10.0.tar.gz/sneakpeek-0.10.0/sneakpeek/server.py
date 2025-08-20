"""SneakPeek API."""

# third-party imports
from fastapi import FastAPI

# app imports
import sneakpeek

app = FastAPI(title="SneakPeek API")


@app.get("/")
def get_link_preview(url: str = None, html: str = None, scrape: bool = False):
    link = sneakpeek.SneakPeek(url=url, html=html, scrape=scrape)
    if url:
        link.fetch()
    return dict(link)


@app.get("/version")
def version():
    return {"sneakpeek": {"version": sneakpeek.__version__}}

