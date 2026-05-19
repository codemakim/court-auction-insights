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



def test_sale_spec_compaction_removes_boilerplate_and_property_display():
    from court_auction_insights.enrichment import _extract_important_sale_spec

    raw = """
# 매각물건명세서
※1: 매각목적물에서 제외되는 미등기건물 등이 있을 경우에는 그 취지를 명확히 기재한다.  2: 매각으로 소멸되는 가등기담보권, 가압류, 전세권의 등기일자가 최선순위 저당권등기일자보다 빠른 경우에는 그 등기일자를 기재한다.
<비고> ※ 최선순위 설정일자보다 대항요건을 먼저 갖춘 주택·상가건물 임차인의 임차보증금은 매수인에게 인수되는 경우가 발생 할 수 있고, 대항력과 우선변제권이 있는 주택·상가건물 임차인이 배당요구를 하였으나 보증금 전액에 관하여 배당을 받지 아니한 경우에는 배당받지 못한 잔액이 매수인에게 인수되게 됨을 주의하시기 바랍니다.
최선순위설정2017.1.31. 근저당권배당요구종기2025. 10. 13.부동산의 점유자와 점유의 권원, 점유할 수 있는 기간, 차임 또는 보증금에 관한 관계인의 진술 및 임차인이 있는 경우 배당요구 여부와 그 일자, 전입신고일자 또는 사업자등록신청일자와 확정일자의 유무와 그 일자점유자성  명점유부분정보출처구 분점유의권 원임대차기간(점유기간)보 증 금차 임전입신고일자·외국인등록(체류지변경신고)일자·사업자등록 신청일자확정일자배당요구여부(배당요구일자)
이병근702호현황조사미상 임차인미상미상미상2024.03.04.미상전부(방2칸)권리신고주거 임차인2023.03.29.부터 2025.08.현재까지200,000,0002024.03.04.2023.03.29.2025.8.27.
부동산의 표시2025타경2408[물건 1] 1. 1동의 건물의 표시 서울특별시 중랑구 망우동 예원캐슬 철근콘크리트구조 12층 도시형생활주택 지3층 136.51㎡ 지2층 87.37㎡ 1층 178.66㎡ 2층 176.72㎡ 감정평가액 252,000,000 회차 기일 최저매각가격 매수신청보증금 1회 2026.04.14 252,000,000
개인정보유출주의 등록자:이영춘, 등록일시:2026.02.05 23:59, 다운로드일시:2026.05.19 23:27
"""

    compact = _extract_important_sale_spec(raw)

    assert "이병근" in compact
    assert "200,000,000" in compact
    assert "최선순위설정2017.1.31" in compact
    assert "매각목적물에서 제외되는 미등기건물" not in compact
    assert "최선순위 설정일자보다 대항요건" not in compact
    assert "부동산의 표시2025타경2408" not in compact
    assert "개인정보유출주의" not in compact
    assert len(compact) < 1800
