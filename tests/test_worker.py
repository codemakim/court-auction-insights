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


def test_worker_marks_newest_non_eligible_auction_as_waiting(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)

    result = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FakeOllamaClient()).run_once()

    assert result.status == "waiting_for_source_document"
    assert get_latest_enrichment(insights_db, 4)["status"] == "waiting_for_source_document"


def test_worker_reaches_downloaded_sale_spec_after_skipping_newer_non_eligible_rows(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    worker = EnrichmentWorker(CrawlerSource(crawler_db), insights_db, FakeOllamaClient())
    worker.run_once()  # auction 4: extraction_failed
    worker.run_once()  # auction 3: not_uploaded

    result = worker.run_once()  # auction 2: downloaded

    row = get_latest_enrichment(insights_db, 2)
    assert result.status == "success"
    assert row["status"] == "success"
    assert row["model_name"] == "gemma4:26b"
