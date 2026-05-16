import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .crawler_source import CrawlerSource
from .db import get_latest_enrichment


def create_app(crawler_db_path: Path, insights_db_path: Path) -> FastAPI:
    app = FastAPI()
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
    source = CrawlerSource(crawler_db_path)

    @app.get("/", response_class=HTMLResponse)
    def list_auctions(request: Request):
        auctions = []
        for auction in source.list_auctions():
            auctions.append({"auction": auction, "enrichment": get_latest_enrichment(insights_db_path, auction.id)})
        return templates.TemplateResponse(request, "auctions.html", {"items": auctions})

    @app.get("/auctions/{auction_id}", response_class=HTMLResponse)
    def auction_detail(request: Request, auction_id: int):
        auction = source.get_auction(auction_id)
        enrichment = get_latest_enrichment(insights_db_path, auction_id)
        bullets = json.loads(enrichment["summary_bullets_json"]) if enrichment else []
        return templates.TemplateResponse(
            request,
            "auction_detail.html",
            {"auction": auction, "enrichment": enrichment, "bullets": bullets},
        )

    return app
