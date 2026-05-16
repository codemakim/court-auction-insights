from court_auction_insights.crawler_source import CrawlerSource


def test_list_auctions_marks_missing_sale_spec_as_not_uploaded(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    assert rows[0].external_key == "2024타경1-1"
    assert rows[0].sale_spec_status == "not_uploaded"
    assert rows[0].sale_spec_markdown is None


def test_list_auctions_returns_downloaded_sale_spec_text(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()

    assert rows[1].external_key == "2024타경2-1"
    assert rows[1].sale_spec_status == "downloaded"
    assert rows[1].sale_spec_markdown == "# markdown"


def test_list_auctions_returns_ordered_image_metadata(crawler_db):
    rows = CrawlerSource(crawler_db).list_auctions()
    assert rows[1].images[0].image_index == 1
    assert rows[1].images[0].alt_text == "전경도_1"
