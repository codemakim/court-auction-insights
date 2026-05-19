from dataclasses import dataclass


@dataclass(frozen=True)
class AuctionImageRecord:
    image_index: int
    alt_text: str | None
    file_path: str
    content_hash: str


@dataclass(frozen=True)
class AuctionSourceRecord:
    id: int
    external_key: str
    case_number: str
    item_number: str
    address: str
    property_category: str
    residential_subtype: str | None
    district: str | None
    appraisal_value: int | None
    minimum_sale_price: int | None
    failed_auction_count: int | None
    sale_date: str | None
    current_status: str | None
    appraisal_summary: str | None
    sale_spec_status: str
    sale_spec_error: str | None
    sale_spec_document_id: int | None
    sale_spec_content_hash: str | None
    sale_spec_markdown: str | None
    area_note: str | None = None
    images: tuple[AuctionImageRecord, ...] = ()
