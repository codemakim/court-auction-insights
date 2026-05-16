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


def test_list_page_shows_representative_image_and_detail_gallery(tmp_path, crawler_db):
    image_root = tmp_path / "images"
    image_path = image_root / "2024타경2-1" / "001.png"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"png")
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auction_images SET file_path = ? WHERE id = 30", (str(image_path),))
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db, image_root))

    list_response = client.get("/")
    detail_response = client.get("/auctions/2")
    media_response = client.get("/media/2/1")

    assert '/media/2/1' in list_response.text
    assert '/media/2/1' in detail_response.text
    assert media_response.status_code == 200


def test_media_route_blocks_files_outside_image_root(tmp_path, crawler_db):
    image_root = tmp_path / "images"
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"png")
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auction_images SET file_path = ? WHERE id = 30", (str(outside),))
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db, image_root))

    response = client.get("/media/2/1")

    assert response.status_code == 404


def test_api_list_and_detail_include_photos(tmp_path, crawler_db):
    image_root = tmp_path / "images"
    image_path = image_root / "2024타경2-1" / "001.png"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"png")
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auction_images SET file_path = ? WHERE id = 30", (str(image_path),))
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db, image_root))

    listing = client.get("/api/auctions").json()
    detail = client.get("/api/auctions/2").json()

    assert listing[1]["images"][0]["url"] == "/media/2/1"
    assert detail["images"][0]["url"] == "/media/2/1"
