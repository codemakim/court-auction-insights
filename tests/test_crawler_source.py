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
