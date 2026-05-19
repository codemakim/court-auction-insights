from court_auction_insights.crawler_source import CrawlerSource


def test_list_auctions_marks_missing_sale_spec_as_not_uploaded(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    row = next(row for row in rows if row.external_key == "2024타경1-1")
    assert row.sale_spec_status == "not_uploaded"
    assert row.sale_spec_markdown is None


def test_list_auctions_returns_downloaded_sale_spec_text(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    row = next(row for row in rows if row.external_key == "2024타경2-1")
    assert row.sale_spec_status == "downloaded"
    assert row.sale_spec_markdown == "# markdown"


def test_list_auctions_returns_ordered_image_metadata(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()
    row = next(row for row in rows if row.external_key == "2024타경2-1")
    assert row.images[0].image_index == 1
    assert row.images[0].alt_text == "전경도_1"


def test_list_auctions_derives_district_and_orders_newest_first(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    assert [row.external_key for row in rows] == ["2024타경3-2", "2024타경3-1", "2024타경2-1", "2024타경1-1"]
    assert rows[0].district == "관악구"
    assert rows[2].district == "동작구"


def test_list_auctions_hides_case_shared_images_for_different_addresses(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    first = next(row for row in rows if row.external_key == "2024타경3-1")
    second = next(row for row in rows if row.external_key == "2024타경3-2")
    assert first.images == ()
    assert second.images == ()


def test_list_auctions_distinguishes_sale_spec_states(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()
    by_key = {row.external_key: row for row in rows}

    assert by_key['2024타경1-1'].sale_spec_status == 'not_uploaded'
    assert by_key['2024타경2-1'].sale_spec_status == 'downloaded'
    assert by_key['2024타경3-2'].sale_spec_status == 'extraction_failed'


def test_list_auctions_decodes_html_entities_in_appraisal_summary(crawler_db):
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auctions SET appraisal_summary = ? WHERE id = 1", ('본건은 &quot;역세권&quot; 인근입니다.',))

    row = next(row for row in CrawlerSource(crawler_db).list_auctions() if row.id == 1)

    assert row.appraisal_summary == '본건은 "역세권" 인근입니다.'


def test_list_auctions_extracts_area_note_from_appraisal_summary(crawler_db):
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute("UPDATE auctions SET appraisal_summary = ? WHERE id = 1", ('대상물건의 집합건축물대장상 대지면적은 263.7㎡입니다.\n다른 문장',))

    row = next(row for row in CrawlerSource(crawler_db).list_auctions() if row.id == 1)

    assert row.area_note == '대상물건의 집합건축물대장상 대지면적은 263.7㎡입니다.'


def test_list_auctions_derives_property_facts_from_address_and_summary(crawler_db):
    import sqlite3
    with sqlite3.connect(crawler_db) as conn:
        conn.execute(
            "UPDATE auctions SET address = ?, appraisal_summary = ? WHERE id = 1",
            (
                '서울특별시 은평구 응암동 176 응암푸르지오 104동 4층402호',
                '철근콘크리트구조 평지붕 15층 건물 내 제4층 제402호로서, (사용승인일 : 2021.2.18) 외벽 마감',
            ),
        )

    row = next(row for row in CrawlerSource(crawler_db).list_auctions() if row.id == 1)

    assert row.neighborhood == '응암동'
    assert row.building_name == '응암푸르지오'
    assert row.floor == 4
    assert row.unit == '402호'
    assert row.total_floors == 15
    assert row.approval_date == '2021.2.18'


def test_list_auctions_leaves_unknown_property_facts_empty(crawler_db):
    row = next(row for row in CrawlerSource(crawler_db).list_auctions() if row.id == 1)

    assert row.building_name is None
    assert row.floor is None
    assert row.total_floors is None
