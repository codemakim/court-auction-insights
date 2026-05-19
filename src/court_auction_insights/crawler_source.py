import html
import re
import sqlite3
from pathlib import Path

from .models import AuctionImageRecord, AuctionSourceRecord


class CrawlerSource:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def list_auctions(self) -> list[AuctionSourceRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(self._query()).fetchall()
            image_rows = conn.execute(self._image_query()).fetchall()
        images = self._group_images(image_rows)
        records = [self._to_record(row, images.get(row["id"], ())) for row in rows]
        return self._suppress_case_shared_images(records)

    def get_auction(self, auction_id: int) -> AuctionSourceRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(self._query("WHERE a.id = ?"), (auction_id,)).fetchone()
            if row is None:
                return None
            case_rows = conn.execute(self._query("WHERE a.case_number = ?"), (row["case_number"],)).fetchall()
            case_ids = tuple(case_row["id"] for case_row in case_rows)
            placeholders = ",".join("?" for _ in case_ids)
            image_rows = conn.execute(
                self._image_query(f"WHERE auction_id IN ({placeholders})"),
                case_ids,
            ).fetchall()
        images = self._group_images(image_rows)
        records = self._suppress_case_shared_images(
            [self._to_record(case_row, images.get(case_row["id"], ())) for case_row in case_rows]
        )
        return next(record for record in records if record.id == auction_id)

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
                a.residential_subtype,
                a.appraisal_value,
                a.minimum_sale_price,
                a.failed_auction_count,
                a.sale_date,
                a.current_status,
                a.appraisal_summary,
                d.id AS sale_spec_document_id,
                d.content_hash AS sale_spec_content_hash,
                d.available AS sale_spec_available,
                d.download_status,
                d.last_download_error,
                dt.extraction_status,
                dt.markdown_text
            FROM auctions a
            LEFT JOIN documents d
                ON d.auction_id = a.id AND d.document_type = 'sale_spec'
            LEFT JOIN document_texts dt
                ON dt.id = (
                    SELECT latest_dt.id
                    FROM document_texts latest_dt
                    WHERE latest_dt.document_id = d.id
                    ORDER BY latest_dt.id DESC
                    LIMIT 1
                )
            {where_clause}
            ORDER BY a.last_seen_at DESC, a.id DESC
        """

    @staticmethod
    def _image_query(where_clause: str = "") -> str:
        return f"SELECT auction_id, image_index, alt_text, file_path, content_hash FROM auction_images {where_clause} ORDER BY auction_id, image_index"

    @staticmethod
    def _group_images(rows: list[sqlite3.Row]) -> dict[int, tuple[AuctionImageRecord, ...]]:
        grouped: dict[int, list[AuctionImageRecord]] = {}
        for row in rows:
            grouped.setdefault(row["auction_id"], []).append(
                AuctionImageRecord(row["image_index"], row["alt_text"], row["file_path"], row["content_hash"])
            )
        return {auction_id: tuple(images) for auction_id, images in grouped.items()}

    @staticmethod
    def _to_record(row: sqlite3.Row, images: tuple[AuctionImageRecord, ...] = ()) -> AuctionSourceRecord:
        if row["sale_spec_document_id"] is None or not row["sale_spec_available"]:
            status = "not_uploaded"
        elif row["download_status"] == "failed":
            status = "download_failed"
        elif row["download_status"] != "downloaded":
            status = "download_pending"
        elif row["extraction_status"] == "extracted":
            status = "downloaded"
        else:
            status = "extraction_failed"

        district_match = re.search(r"([가-힣]+구)", row["address"])
        appraisal_summary = html.unescape(row["appraisal_summary"]) if row["appraisal_summary"] else None
        property_facts = CrawlerSource._extract_property_facts(row["address"], appraisal_summary)
        return AuctionSourceRecord(
            id=row["id"],
            external_key=row["external_key"],
            case_number=row["case_number"],
            item_number=row["item_number"],
            address=row["address"],
            property_category=row["property_category"],
            residential_subtype=row["residential_subtype"],
            district=district_match.group(1) if district_match else None,
            appraisal_value=row["appraisal_value"],
            minimum_sale_price=row["minimum_sale_price"],
            failed_auction_count=row["failed_auction_count"],
            sale_date=row["sale_date"],
            current_status=row["current_status"],
            appraisal_summary=appraisal_summary,
            area_note=CrawlerSource._extract_area_note(appraisal_summary),
            neighborhood=property_facts["neighborhood"],
            building_name=property_facts["building_name"],
            floor=property_facts["floor"],
            unit=property_facts["unit"],
            total_floors=property_facts["total_floors"],
            approval_date=property_facts["approval_date"],
            sale_spec_status=status,
            sale_spec_error=row["last_download_error"],
            sale_spec_document_id=row["sale_spec_document_id"],
            sale_spec_content_hash=row["sale_spec_content_hash"],
            sale_spec_markdown=row["markdown_text"],
            images=images,
        )

    @staticmethod
    def _extract_property_facts(address: str, appraisal_summary: str | None) -> dict[str, object | None]:
        neighborhood_match = re.search(r"([가-힣]+동)", address)
        floor_match = re.search(r"(\d+)층", address)
        unit_match = re.search(r"(\d+호)", address)
        building_name = None
        if neighborhood_match:
            after_neighborhood = address[neighborhood_match.end():].strip()
            after_lot = re.sub(r"^[0-9산\-]+\s*", "", after_neighborhood)
            building_match = re.match(r"(.+?)(?:\s+\d+동|\s+\d+층|\s+\d+호|$)", after_lot)
            if building_match:
                candidate = building_match.group(1).strip(" ,")
                building_name = candidate or None
        summary = appraisal_summary or ""
        total_floors_match = re.search(r"(\d+)층\s*건물", summary)
        approval_match = re.search(r"사용승인일\s*[:：]?\s*(\d{4}[.]\d{1,2}[.]\d{1,2})", summary)
        return {
            "neighborhood": neighborhood_match.group(1) if neighborhood_match else None,
            "building_name": building_name,
            "floor": int(floor_match.group(1)) if floor_match else None,
            "unit": unit_match.group(1) if unit_match else None,
            "total_floors": int(total_floors_match.group(1)) if total_floors_match else None,
            "approval_date": approval_match.group(1) if approval_match else None,
        }

    @staticmethod
    def _extract_area_note(appraisal_summary: str | None) -> str | None:
        if not appraisal_summary:
            return None
        keywords = ("전유면적", "전용면적", "공급면적", "건물면적", "대지권", "대지면적", "면적은", "㎡")
        for line in (line.strip() for line in appraisal_summary.splitlines()):
            if line and any(keyword in line for keyword in keywords):
                return line
        return None

    @staticmethod
    def _suppress_case_shared_images(records: list[AuctionSourceRecord]) -> list[AuctionSourceRecord]:
        by_case: dict[str, list[AuctionSourceRecord]] = {}
        for record in records:
            by_case.setdefault(record.case_number, []).append(record)

        shared_ids: set[int] = set()
        for case_records in by_case.values():
            by_signature: dict[tuple[str, ...], list[AuctionSourceRecord]] = {}
            for record in case_records:
                if not record.images:
                    continue
                signature = tuple(image.content_hash for image in record.images)
                by_signature.setdefault(signature, []).append(record)
            for same_images in by_signature.values():
                if len(same_images) < 2:
                    continue
                if len({record.address for record in same_images}) > 1:
                    shared_ids.update(record.id for record in same_images)

        return [
            AuctionSourceRecord(
                **{
                    **record.__dict__,
                    "images": () if record.id in shared_ids else record.images,
                }
            )
            for record in records
        ]
