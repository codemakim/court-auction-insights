from pathlib import Path

from court_auction_insights.db import (
    get_latest_enrichment,
    init_db,
    mark_stale_if_source_changed,
    save_enrichment,
)


def test_enrichment_persistence_and_staleness(tmp_path: Path):
    db_path = tmp_path / "insights.db"
    init_db(db_path)
    save_enrichment(
        db_path,
        auction_id=1,
        source_document_id=10,
        model_name="gemma4:26b",
        prompt_version="v1",
        schema_version="v1",
        status="success",
        source_hash="abc",
        summary_title="요약",
        summary_bullets=["bullet"],
        risk_label="review_recommended",
        risk_comment="확인 필요",
        mobile_card={"title": "요약"},
    )

    row = get_latest_enrichment(db_path, 1)
    assert row is not None
    assert row["status"] == "success"

    changed = mark_stale_if_source_changed(db_path, 1, "def")
    assert changed is True
    assert get_latest_enrichment(db_path, 1)["status"] == "stale"


def test_ollama_client_builds_compact_prompt(monkeypatch):
    from court_auction_insights.enrichment import OllamaClient
    from court_auction_insights.models import AuctionSourceRecord
    captured = {}

    class Response:
        def raise_for_status(self): pass
        def json(self):
            return {"message": {"content": '{"summary_title":"t","summary_bullets":[],"risk_label":"unknown","risk_comment":"c","mobile_highlights":[]}'}}

    def fake_post(url, json, timeout):
        captured["json"] = json
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("court_auction_insights.enrichment.requests.post", fake_post)
    auction = AuctionSourceRecord(
        id=1, external_key="k", case_number="c", item_number="1", address="서울",
        property_category="건물", residential_subtype="아파트", district="강남구",
        appraisal_value=200, minimum_sale_price=100, failed_auction_count=1,
        sale_date="2026-05-19", current_status="매각기일", appraisal_summary="감정요약" * 1000,
        sale_spec_status="downloaded", sale_spec_error=None, sale_spec_document_id=1,
        sale_spec_content_hash="h", sale_spec_markdown="명세서" * 10000,
        area_note="전유부분 81.31㎡", building_name="현대파크아파트", floor=4, unit="401호",
        total_floors=6, approval_date="1993.01.01",
    )

    OllamaClient("http://ollama", "gemma4:26b", timeout_seconds=600).enrich(auction)

    content = captured["json"]["messages"][1]["content"]
    assert captured["timeout"] == 600
    assert len(content) < 9000
    assert "현대파크아파트" in content
    assert "전유부분 81.31㎡" in content
