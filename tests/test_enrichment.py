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
