import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .crawler_source import CrawlerSource
from .db import get_latest_enrichment


def create_app(crawler_db_path: Path, insights_db_path: Path, crawler_image_root: Path | None = None) -> FastAPI:
    app = FastAPI()
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
    source = CrawlerSource(crawler_db_path)
    image_root = Path(crawler_image_root or "/var/lib/court-auction-collector/data/images").resolve()


    def serialize_auction(auction, enrichment=None):
        return {
            "id": auction.id,
            "external_key": auction.external_key,
            "case_number": auction.case_number,
            "item_number": auction.item_number,
            "address": auction.address,
            "property_category": auction.property_category,
            "minimum_sale_price": auction.minimum_sale_price,
            "sale_date": auction.sale_date,
            "current_status": auction.current_status,
            "sale_spec_status": auction.sale_spec_status,
            "images": [
                {
                    "image_index": image.image_index,
                    "alt_text": image.alt_text,
                    "url": f"/media/{auction.id}/{image.image_index}",
                }
                for image in auction.images
            ],
            "enrichment": dict(enrichment) if enrichment is not None else None,
        }

    @app.get("/api/auctions")
    def api_list_auctions():
        return [
            serialize_auction(auction, get_latest_enrichment(insights_db_path, auction.id))
            for auction in source.list_auctions()
        ]

    @app.get("/api/auctions/{auction_id}")
    def api_auction_detail(auction_id: int):
        auction = source.get_auction(auction_id)
        if auction is None:
            raise HTTPException(status_code=404)
        return serialize_auction(auction, get_latest_enrichment(insights_db_path, auction_id))

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

    @app.get("/media/{auction_id}/{image_index}")
    def media(auction_id: int, image_index: int):
        auction = source.get_auction(auction_id)
        if auction is None:
            raise HTTPException(status_code=404)
        image = next((image for image in auction.images if image.image_index == image_index), None)
        if image is None:
            raise HTTPException(status_code=404)
        path = Path(image.file_path).resolve()
        try:
            path.relative_to(image_root)
        except ValueError:
            raise HTTPException(status_code=404)
        if not path.exists():
            raise HTTPException(status_code=404)
        return FileResponse(path)

    return app
