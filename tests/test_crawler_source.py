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

    assert [row.external_key for row in rows] == ["2024타경2-1", "2024타경1-1"]
    assert rows[0].district == "동작구"
    assert rows[1].district == "관악구"
