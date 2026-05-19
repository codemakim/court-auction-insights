import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .crawler_source import CrawlerSource
from .db import get_latest_enrichment


def create_app(crawler_db_path: Path, insights_db_path: Path, crawler_image_root: Path | None = None) -> FastAPI:
    app = FastAPI()
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
    source = CrawlerSource(crawler_db_path)
    image_root = Path(crawler_image_root or "/var/lib/court-auction-collector/data/images").resolve()


    def derived_metrics(auction):
        discount_rate = None
        price_gap = None
        if auction.appraisal_value and auction.minimum_sale_price is not None:
            price_gap = auction.appraisal_value - auction.minimum_sale_price
            discount_rate = round((1 - auction.minimum_sale_price / auction.appraisal_value) * 100)
        return discount_rate, price_gap

    def serialize_auction(auction, enrichment=None):
        discount_rate, price_gap = derived_metrics(auction)
        return {
            "id": auction.id,
            "external_key": auction.external_key,
            "case_number": auction.case_number,
            "item_number": auction.item_number,
            "address": auction.address,
            "property_category": auction.property_category,
            "residential_subtype": auction.residential_subtype,
            "district": auction.district,
            "appraisal_value": auction.appraisal_value,
            "minimum_sale_price": auction.minimum_sale_price,
            "failed_auction_count": auction.failed_auction_count,
            "sale_date": auction.sale_date,
            "current_status": auction.current_status,
            "appraisal_summary": auction.appraisal_summary,
            "area_note": auction.area_note,
            "neighborhood": auction.neighborhood,
            "building_name": auction.building_name,
            "floor": auction.floor,
            "unit": auction.unit,
            "total_floors": auction.total_floors,
            "approval_date": auction.approval_date,
            "sale_spec_status": auction.sale_spec_status,
            "sale_spec_error": auction.sale_spec_error,
            "sale_spec_markdown": auction.sale_spec_markdown,
            "discount_rate": discount_rate,
            "price_gap": price_gap,
            "image_count": len(auction.images),
            "images": [
                {
                    "image_index": image.image_index,
                    "alt_text": image.alt_text,
                    "url": f"/media/{auction.id}/{image.image_index}",
                }
                for image in auction.images
            ],
            "enrichment": dict(enrichment) if enrichment is not None else None,
            "enrichment_status": "completed" if enrichment is not None else "pending",
        }


    @app.get("/api/summary")
    def api_summary():
        auctions = [
            serialize_auction(auction, get_latest_enrichment(insights_db_path, auction.id))
            for auction in source.list_auctions()
        ]
        sale_spec_status_counts = {}
        enrichment_status_counts = {}
        district_counts = {}
        subtype_counts = {}
        image_count = 0
        derived_fact_count = 0
        min_price = None
        max_price = None
        for item in auctions:
            sale_spec_status_counts[item["sale_spec_status"]] = sale_spec_status_counts.get(item["sale_spec_status"], 0) + 1
            enrichment_status_counts[item["enrichment_status"]] = enrichment_status_counts.get(item["enrichment_status"], 0) + 1
            if item["district"]:
                district_counts[item["district"]] = district_counts.get(item["district"], 0) + 1
            if item["residential_subtype"]:
                subtype_counts[item["residential_subtype"]] = subtype_counts.get(item["residential_subtype"], 0) + 1
            image_count += item["image_count"]
            if item["building_name"] or item["floor"] or item["approval_date"] or item["area_note"]:
                derived_fact_count += 1
            price = item["minimum_sale_price"]
            if price is not None:
                min_price = price if min_price is None else min(min_price, price)
                max_price = price if max_price is None else max(max_price, price)
        return {
            "total_count": len(auctions),
            "sale_spec_status_counts": sale_spec_status_counts,
            "enrichment_status_counts": enrichment_status_counts,
            "district_counts": district_counts,
            "subtype_counts": subtype_counts,
            "districts": sorted(district_counts),
            "subtypes": sorted(subtype_counts),
            "image_count": image_count,
            "derived_fact_count": derived_fact_count,
            "min_price": min_price,
            "max_price": max_price,
        }

    @app.get("/api/auctions")
    def api_list_auctions(
        q: str | None = Query(default=None),
        district: str | None = Query(default=None),
        subtype: str | None = Query(default=None),
        min_price: int | None = Query(default=None),
        max_price: int | None = Query(default=None),
        sale_spec_status: str | None = Query(default=None),
        enrichment_status: str | None = Query(default=None),
        sort: str = Query(default="latest"),
    ):
        items = [
            serialize_auction(auction, get_latest_enrichment(insights_db_path, auction.id))
            for auction in source.list_auctions()
        ]
        if q:
            needle = q.casefold()
            items = [
                item for item in items
                if needle in item["address"].casefold()
                or needle in item["case_number"].casefold()
                or needle in item["external_key"].casefold()
            ]
        if district:
            items = [item for item in items if item["district"] == district]
        if subtype:
            items = [item for item in items if item["residential_subtype"] == subtype]
        if min_price is not None:
            items = [item for item in items if item["minimum_sale_price"] is not None and item["minimum_sale_price"] >= min_price]
        if max_price is not None:
            items = [item for item in items if item["minimum_sale_price"] is not None and item["minimum_sale_price"] <= max_price]
        if sale_spec_status:
            items = [item for item in items if item["sale_spec_status"] == sale_spec_status]
        if enrichment_status:
            items = [item for item in items if item["enrichment_status"] == enrichment_status]
        if sort == "price_asc":
            items.sort(key=lambda item: (item["minimum_sale_price"] is None, item["minimum_sale_price"] or 0))
        elif sort == "price_desc":
            items.sort(key=lambda item: (item["minimum_sale_price"] is None, -(item["minimum_sale_price"] or 0)))
        elif sort == "sale_date_asc":
            items.sort(key=lambda item: (item["sale_date"] is None, item["sale_date"] or ""))
        return items

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
