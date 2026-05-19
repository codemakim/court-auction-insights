from court_auction_insights.crawler_source import CrawlerSource
from court_auction_insights.db import get_latest_enrichment, init_db
from court_auction_insights.worker import EnrichmentWorker


class FakeOllamaClient:
    def enrich(self, auction):
        return {
            "summary_title": "서울시 B",
            "summary_bullets": ["명세서 있음"],
            "risk_label": "review_recommended",
            "risk_comment": "사람 확인 권장",
            "mobile_highlights": ["명세서 있음"],
        }


def test_worker_processes_first_downloaded_sale_spec_without_waiting_records(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)

    result = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FakeOllamaClient()).run_once()

    row = get_latest_enrichment(insights_db, 2)
    assert result.status == "success"
    assert result.auction_id == 2
    assert row["status"] == "success"
    assert row["model_name"] == "gemma4:26b"
    assert get_latest_enrichment(insights_db, 4) is None


def test_worker_skips_waiting_rows_and_processes_downloaded_sale_spec(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)

    result = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FakeOllamaClient()).run_once()

    assert result.status == "success"
    assert result.auction_id == 2
    assert get_latest_enrichment(insights_db, 4) is None
    assert get_latest_enrichment(insights_db, 3) is None
    assert get_latest_enrichment(insights_db, 2)["status"] == "success"


def test_worker_waiting_record_does_not_block_later_downloaded_document(tmp_path, crawler_db):
    from court_auction_insights.db import save_enrichment
    import sqlite3
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    save_enrichment(
        insights_db,
        auction_id=1,
        source_document_id=None,
        model_name="gemma4:26b",
        prompt_version="v1",
        schema_version="v1",
        status="waiting_for_source_document",
        source_hash=None,
    )
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("INSERT INTO documents VALUES (12, 1, 'sale_spec', 1, '매각물건명세서', '/tmp/spec.pdf', '2026-05-16', 'downloaded', 'newhash', 1, '2026-05-16', NULL)")
        conn.execute("INSERT INTO document_texts VALUES (22, 12, 'extracted', 'raw text', '# newly downloaded', '2026-05-16', 'v1')")

    worker = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FakeOllamaClient())
    worker.run_once()  # auction 2 first
    result = worker.run_once()  # auction 1 should not be blocked by previous waiting row

    assert result.status == "success"
    assert result.auction_id == 1
    assert get_latest_enrichment(insights_db, 1)["source_hash"] == "newhash"


def test_worker_records_failed_enrichment_when_model_raises(tmp_path, crawler_db):
    class FailingClient:
        def enrich(self, auction):
            raise RuntimeError("model timeout")

    insights_db = tmp_path / "insights.db"
    init_db(insights_db)

    result = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FailingClient()).run_once()

    row = get_latest_enrichment(insights_db, 2)
    assert result.status == "failed"
    assert row["status"] == "failed"
    assert "model timeout" in row["error_message"]
