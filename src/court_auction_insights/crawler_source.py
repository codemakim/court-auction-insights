import sqlite3
from pathlib import Path

from .models import AuctionSourceRecord


class CrawlerSource:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def list_auctions(self) -> list[AuctionSourceRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(self._query()).fetchall()
        return [self._to_record(row) for row in rows]

    def get_auction(self, auction_id: int) -> AuctionSourceRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(self._query("WHERE a.id = ?"), (auction_id,)).fetchone()
        return self._to_record(row) if row else None

    @staticmethod
    def _query(where_clause: str = "") -> str:
        return f"""
            SELECT
                a.id,
                a.external_key,
                a.case_number,
                a.item_number,
                a.address,
                a.property_category,
                a.minimum_sale_price,
                a.sale_date,
                a.current_status,
                d.id AS sale_spec_document_id,
                d.content_hash AS sale_spec_content_hash,
                d.download_status,
                dt.extraction_status,
                dt.markdown_text
            FROM auctions a
            LEFT JOIN documents d
                ON d.auction_id = a.id AND d.document_type = 'sale_spec'
            LEFT JOIN document_texts dt
                ON dt.document_id = d.id
            {where_clause}
            ORDER BY a.id
        """

    @staticmethod
    def _to_record(row: sqlite3.Row) -> AuctionSourceRecord:
        if row["sale_spec_document_id"] is None:
            status = "not_uploaded"
        elif row["download_status"] == "downloaded" and row["extraction_status"] == "extracted":
            status = "downloaded"
        else:
            status = "extraction_failed"

        return AuctionSourceRecord(
            id=row["id"],
            external_key=row["external_key"],
            case_number=row["case_number"],
            item_number=row["item_number"],
            address=row["address"],
            property_category=row["property_category"],
            minimum_sale_price=row["minimum_sale_price"],
            sale_date=row["sale_date"],
            current_status=row["current_status"],
            sale_spec_status=status,
            sale_spec_document_id=row["sale_spec_document_id"],
            sale_spec_content_hash=row["sale_spec_content_hash"],
            sale_spec_markdown=row["markdown_text"],
        )
