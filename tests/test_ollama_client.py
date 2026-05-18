from court_auction_insights.enrichment import OllamaClient
from court_auction_insights.models import AuctionSourceRecord


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "message": {
                "content": '{"summary_title":"요약","summary_bullets":[],"risk_label":"low_signal","risk_comment":"확인","mobile_highlights":[]}'
            }
        }


def test_ollama_client_parses_structured_json(monkeypatch):
    monkeypatch.setattr("court_auction_insights.enrichment.requests.post", lambda *args, **kwargs: FakeResponse())
    auction = AuctionSourceRecord(
        id=1,
        external_key="k",
        case_number="c",
        item_number="1",
        address="서울",
        property_category="건물",
        residential_subtype="아파트",
        district=None,
        appraisal_value=2,
        minimum_sale_price=1,
        failed_auction_count=0,
        sale_date=None,
        current_status=None,
        appraisal_summary=None,
        sale_spec_status="downloaded",
        sale_spec_error=None,
        sale_spec_document_id=1,
        sale_spec_content_hash="h",
        sale_spec_markdown="# md",
    )

    result = OllamaClient("http://127.0.0.1:11434", "gemma4:26b").enrich(auction)

    assert result["summary_title"] == "요약"
