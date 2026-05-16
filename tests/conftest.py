import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def crawler_db(tmp_path: Path) -> Path:
    path = tmp_path / "crawler.sqlite3"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE auctions (
            id INTEGER PRIMARY KEY,
            external_key TEXT NOT NULL,
            case_number TEXT NOT NULL,
            item_number TEXT NOT NULL,
            address TEXT NOT NULL,
            property_category TEXT NOT NULL,
            residential_subtype TEXT,
            appraisal_value INTEGER,
            minimum_sale_price INTEGER,
            failed_auction_count INTEGER,
            sale_date TEXT,
            current_status TEXT,
            appraisal_summary TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL
        );
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            auction_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            available INTEGER NOT NULL,
            source_label TEXT,
            file_path TEXT,
            downloaded_at TEXT,
            download_status TEXT NOT NULL,
            content_hash TEXT,
            download_attempt_count INTEGER NOT NULL,
            last_download_attempt_at TEXT,
            last_download_error TEXT
        );
        CREATE TABLE auction_images (
            id INTEGER PRIMARY KEY,
            auction_id INTEGER NOT NULL,
            image_index INTEGER NOT NULL,
            alt_text TEXT,
            file_path TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            byte_size INTEGER NOT NULL,
            downloaded_at TEXT NOT NULL
        );
        CREATE TABLE document_texts (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL,
            extraction_status TEXT NOT NULL,
            extracted_text TEXT,
            markdown_text TEXT,
            processed_at TEXT NOT NULL,
            processor_version TEXT NOT NULL
        );
        """
    )
    conn.executemany(
        """
        INSERT INTO auctions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "2024타경1-1", "2024타경1", "1", "서울시 A", "아파트", None, 100, 80, 1, "2026-06-01", "매각기일", None, "2026-05-01", "2026-05-16"),
            (2, "2024타경2-1", "2024타경2", "1", "서울시 B", "아파트", None, 200, 160, 0, "2026-06-02", "매각기일", None, "2026-05-01", "2026-05-16"),
        ],
    )
    conn.execute(
        """
        INSERT INTO documents VALUES (10, 2, 'sale_spec', 1, '매각물건명세서', '/tmp/spec.pdf', '2026-05-16', 'downloaded', 'abc123', 1, '2026-05-16', NULL)
        """
    )
    conn.execute(
        """
        INSERT INTO document_texts VALUES (20, 10, 'extracted', 'raw text', '# markdown', '2026-05-16', 'v1')
        """
    )
    conn.execute(
        """
        INSERT INTO auction_images VALUES (30, 2, 1, '전경도_1', '/tmp/images/2024타경2-1/001.png', 'hash', 123, '2026-05-16')
        """
    )
    conn.commit()
    conn.close()
    return path
