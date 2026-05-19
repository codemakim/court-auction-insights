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

    item = next(item for item in listing if item["id"] == 2)
    assert item["images"][0]["url"] == "/media/2/1"
    assert detail["images"][0]["url"] == "/media/2/1"


def test_api_list_supports_filters_sort_and_enrichment_status(tmp_path, crawler_db):
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

    filtered = client.get(
        "/api/auctions",
        params={
            "q": "사당동",
            "district": "동작구",
            "subtype": "다세대",
            "min_price": 100,
            "max_price": 200,
            "sale_spec_status": "downloaded",
            "enrichment_status": "completed",
        },
    ).json()
    pending = client.get("/api/auctions", params={"enrichment_status": "pending"}).json()
    price_asc = client.get("/api/auctions", params={"sort": "price_asc"}).json()

    assert [item["external_key"] for item in filtered] == ["2024타경2-1"]
    assert filtered[0]["district"] == "동작구"
    assert filtered[0]["enrichment_status"] == "completed"
    assert [item["external_key"] for item in pending] == ["2024타경3-2", "2024타경3-1", "2024타경1-1"]
    assert [item["external_key"] for item in price_asc] == ["2024타경1-1", "2024타경2-1", "2024타경3-1", "2024타경3-2"]


def test_api_detail_serializes_pending_enrichment_state(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    detail = client.get("/api/auctions/1").json()

    assert detail["district"] == "관악구"
    assert detail["enrichment_status"] == "pending"


def test_api_list_filters_extraction_failed_sale_specs(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    items = client.get("/api/auctions", params={"sale_spec_status": "extraction_failed"}).json()

    assert [item["external_key"] for item in items] == ["2024타경3-2"]


def test_api_detail_includes_review_fields(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    detail = client.get("/api/auctions/2").json()

    assert detail["appraisal_value"] == 200
    assert detail["failed_auction_count"] == 0
    assert detail["appraisal_summary"] is None
    assert detail["sale_spec_status"] == "downloaded"


def test_api_summary_exposes_collected_data_shape(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    summary = client.get("/api/summary").json()

    assert summary["total_count"] == 4
    assert summary["sale_spec_status_counts"]["downloaded"] == 1
    assert summary["sale_spec_status_counts"]["not_uploaded"] == 2
    assert summary["enrichment_status_counts"]["pending"] == 4
    assert summary["image_count"] == 1
    assert "관악구" in summary["districts"]


def test_api_detail_includes_sale_spec_markdown_and_discount_fields(tmp_path, crawler_db):
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    detail = client.get("/api/auctions/2").json()

    assert detail["sale_spec_markdown"] == "# markdown"
    assert detail["discount_rate"] == 20
    assert detail["price_gap"] == 40
    assert detail["image_count"] == 1


def test_api_detail_decodes_summary_and_includes_area_note(tmp_path, crawler_db):
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auctions SET appraisal_summary = ? WHERE id = 1", ('본건은 &quot;역세권&quot;입니다.\n대지권 면적은 31.25㎡입니다.',))
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    detail = client.get("/api/auctions/1").json()

    assert detail["appraisal_summary"].startswith('본건은 "역세권"입니다.')
    assert detail["area_note"] == '대지권 면적은 31.25㎡입니다.'


def test_api_detail_includes_derived_property_facts(tmp_path, crawler_db):
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute(
            "UPDATE auctions SET address = ?, appraisal_summary = ? WHERE id = 1",
            (
                '서울특별시 은평구 응암동 176 응암푸르지오 104동 4층402호',
                '철근콘크리트구조 평지붕 15층 건물 내 제4층 제402호로서, (사용승인일 : 2021.2.18) 외벽 마감',
            ),
        )
    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    client = TestClient(create_app(crawler_db, insights_db))

    detail = client.get("/api/auctions/1").json()

    assert detail["neighborhood"] == '응암동'
    assert detail["building_name"] == '응암푸르지오'
    assert detail["floor"] == 4
    assert detail["unit"] == '402호'
    assert detail["total_floors"] == 15
    assert detail["approval_date"] == '2021.2.18'



def test_api_reports_only_successful_enrichments_as_completed(tmp_path, crawler_db):
    from fastapi.testclient import TestClient
    from court_auction_insights.db import init_db, save_enrichment
    from court_auction_insights.web import create_app

    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    save_enrichment(
        insights_db,
        auction_id=2,
        source_document_id=10,
        model_name="gemma4:26b",
        prompt_version="v3",
        schema_version="v1",
        status="success",
        source_hash="abc123",
        summary_title="요약 완료",
        summary_bullets=["핵심"],
        risk_label="review_recommended",
        risk_comment="검토 필요",
    )
    save_enrichment(
        insights_db,
        auction_id=4,
        source_document_id=11,
        model_name="gemma4:26b",
        prompt_version="v3",
        schema_version="v1",
        status="failed",
        source_hash="def456",
        error_message="timeout",
    )

    client = TestClient(create_app(crawler_db, insights_db, tmp_path))

    summary = client.get("/api/summary").json()
    assert summary["enrichment_status_counts"] == {"completed": 1, "pending": 2, "failed": 1}

    success = client.get("/api/auctions/2").json()
    failed = client.get("/api/auctions/4").json()
    assert success["enrichment_status"] == "completed"
    assert success["enrichment"]["summary_title"] == "요약 완료"
    assert failed["enrichment_status"] == "failed"
    assert failed["enrichment"] is None
    assert failed["enrichment_error"] == "timeout"



def test_api_sanitizes_existing_html_in_enrichment(tmp_path, crawler_db):
    from fastapi.testclient import TestClient
    from court_auction_insights.db import init_db, save_enrichment
    from court_auction_insights.web import create_app

    insights_db = tmp_path / "insights.db"
    init_db(insights_db)
    save_enrichment(
        insights_db,
        auction_id=2,
        source_document_id=10,
        model_name="gemma4:26b",
        prompt_version="v2",
        schema_version="v1",
        status="success",
        source_hash="abc123",
        summary_title="<b>금천구 가산동</b>",
        summary_bullets=["<i>임차인 없음</i>"],
        risk_label="low",
        risk_comment="<strong>낮음</strong>",
    )

    data = TestClient(create_app(crawler_db, insights_db, tmp_path)).get("/api/auctions/2").json()

    assert data["enrichment"]["summary_title"] == "금천구 가산동"
    assert data["enrichment"]["summary_bullets_json"] == '["임차인 없음"]'
    assert data["enrichment"]["risk_comment"] == "낮음"
