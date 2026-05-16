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
    auction = AuctionSourceRecord(1, "k", "c", "1", "서울", "아파트", 1, None, None, "downloaded", 1, "h", "# md")

    result = OllamaClient("http://127.0.0.1:11434", "gemma4:26b").enrich(auction)

    assert result["summary_title"] == "요약"
