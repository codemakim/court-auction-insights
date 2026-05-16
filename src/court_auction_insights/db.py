import json
import sqlite3
from datetime import datetime, UTC
from pathlib import Path


def init_db(path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS auction_enrichments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auction_id INTEGER NOT NULL,
                source_document_id INTEGER,
                model_name TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                schema_version TEXT NOT NULL,
                status TEXT NOT NULL,
                summary_title TEXT,
                summary_bullets_json TEXT,
                risk_label TEXT,
                risk_comment TEXT,
                mobile_card_json TEXT,
                source_hash TEXT,
                generated_at TEXT NOT NULL,
                error_message TEXT
            )
            """
        )


def save_enrichment(
    path: Path,
    *,
    auction_id: int,
    source_document_id: int | None,
    model_name: str,
    prompt_version: str,
    schema_version: str,
    status: str,
    source_hash: str | None,
    summary_title: str | None = None,
    summary_bullets: list[str] | None = None,
    risk_label: str | None = None,
    risk_comment: str | None = None,
    mobile_card: dict | None = None,
    error_message: str | None = None,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO auction_enrichments (
                auction_id, source_document_id, model_name, prompt_version, schema_version,
                status, summary_title, summary_bullets_json, risk_label, risk_comment,
                mobile_card_json, source_hash, generated_at, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                auction_id,
                source_document_id,
                model_name,
                prompt_version,
                schema_version,
                status,
                summary_title,
                json.dumps(summary_bullets or [], ensure_ascii=False),
                risk_label,
                risk_comment,
                json.dumps(mobile_card or {}, ensure_ascii=False),
                source_hash,
                datetime.now(UTC).isoformat(),
                error_message,
            ),
        )


def get_latest_enrichment(path: Path, auction_id: int):
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM auction_enrichments WHERE auction_id = ? ORDER BY id DESC LIMIT 1",
            (auction_id,),
        ).fetchone()


def mark_stale_if_source_changed(path: Path, auction_id: int, source_hash: str | None) -> bool:
    row = get_latest_enrichment(path, auction_id)
    if row is None or row["source_hash"] == source_hash or row["status"] == "stale":
        return False
    with sqlite3.connect(path) as conn:
        conn.execute("UPDATE auction_enrichments SET status = 'stale' WHERE id = ?", (row["id"],))
    return True
