from fastapi.testclient import TestClient

from court_auction_insights.db import init_db, save_enrichment
from court_auction_insights.web import create_app


def test_list_page_shows_missing_sale_spec_badge(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    response = client.get("/")

    assert response.status_code == 200
    assert "매각물건명세서 미업로드" in response.text


def test_detail_page_shows_summary_when_enrichment_exists(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    save_enrichment(
        insights_db,
        auction_id=2,
        source_document_id=10,
        model_name="gemma4:26b",
        prompt_version="v1",
        schema_version="v1",
        status="success",
        source_hash="abc123",
        summary_title="서울시 B",
        summary_bullets=["명세서 있음"],
        risk_label="review_recommended",
        risk_comment="사람 확인 권장",
        mobile_card={},
    )
    client = TestClient(create_app(crawler_db, insights_db))

    response = client.get("/auctions/2")

    assert response.status_code == 200
    assert "서울시 B" in response.text
    assert "사람 확인 권장" in response.text
