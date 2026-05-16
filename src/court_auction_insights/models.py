from dataclasses import dataclass


@dataclass(frozen=True)
class AuctionImageRecord:
    image_index: int
    alt_text: str | None
    file_path: str


@dataclass(frozen=True)
class AuctionSourceRecord:
    id: int
    external_key: str
    case_number: str
    item_number: str
    address: str
    property_category: str
    minimum_sale_price: int | None
    sale_date: str | None
    current_status: str | None
    sale_spec_status: str
    sale_spec_document_id: int | None
    sale_spec_content_hash: str | None
    sale_spec_markdown: str | None
    images: tuple[AuctionImageRecord, ...] = ()
