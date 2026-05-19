import json
import re
from typing import Any

import requests


BOILERPLATE_PATTERNS = [
    r"개인정보유출주의[^\n]*",
    r"등록자:[^\n]*",
    r"다운로드일시:[^\n]*",
    r"※1:.*?기재한다\.",
    r"2: 매각으로 소멸되는.*?기재한다\.",
    r"<비고> ※ 최선순위 설정일자보다.*?주의하시기 바랍니다\.",
    r"서 울 중 앙 지 방 법 원 매각물건명세서",
]

IMPORTANT_KEYWORDS = (
    "지분매각",
    "특별매각조건",
    "공유자",
    "우선매수",
    "점유",
    "임차",
    "대항",
    "배당",
    "전입",
    "확정일자",
    "보증금",
    "차임",
    "전유부분",
    "대지권",
    "최저매각가격",
    "회차",
    "기일",
    "유찰",
    "매각지분",
    "조사된 임차내역",
    "최선순위",
    "특별매각",
)


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def _strip_boilerplate(text: str) -> str:
    cleaned = text or ""
    for pattern in BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.DOTALL)
    cleaned = cleaned.replace("---------------------------------------------------", " ")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _trim(text: str | None, limit: int) -> str | None:
    if not text:
        return None
    text = _collapse_whitespace(text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def _extract_important_sale_spec(markdown: str | None, *, limit: int = 5200) -> str | None:
    if not markdown:
        return None
    cleaned = _strip_boilerplate(markdown)
    lines = [_collapse_whitespace(line) for line in cleaned.splitlines()]
    lines = [line for line in lines if line]

    important: list[str] = []
    for line in lines:
        if any(keyword in line for keyword in IMPORTANT_KEYWORDS):
            important.append(line)

    # 명세서 OCR/텍스트 추출은 줄 구분이 깨지는 경우가 많아서, 키워드 라인만으로
    # 부족하면 정제된 앞부분도 함께 넣는다. 그래도 반복 양식은 제거된 상태다.
    joined = "\n".join(dict.fromkeys(important))
    if len(joined) < 1500:
        prefix = "\n".join(lines[:80])
        joined = f"{joined}\n\n[정제 원문 앞부분]\n{prefix}" if joined else prefix

    if len(joined) > limit:
        joined = joined[:limit].rstrip() + "…"
    return joined


def build_compact_auction_payload(auction: Any) -> dict[str, Any]:
    return {
        "기본정보": {
            "수집키": auction.external_key,
            "사건번호": auction.case_number,
            "물건번호": auction.item_number,
            "주소": auction.address,
            "구": auction.district,
            "동": auction.neighborhood,
            "건물명": auction.building_name,
            "층": auction.floor,
            "호수": auction.unit,
            "총층수": auction.total_floors,
            "사용승인일": auction.approval_date,
            "종류": auction.property_category,
            "주거세부유형": auction.residential_subtype,
        },
        "가격_일정": {
            "감정가": auction.appraisal_value,
            "최저매각가": auction.minimum_sale_price,
            "유찰횟수": auction.failed_auction_count,
            "매각기일": auction.sale_date,
            "현재상태": auction.current_status,
        },
        "면적_요약": auction.area_note,
        "감정평가_요약": _trim(auction.appraisal_summary, 1800),
        "매각물건명세서_핵심발췌": _extract_important_sale_spec(auction.sale_spec_markdown),
    }


class OllamaClient:
    def __init__(self, base_url: str, model_name: str, *, timeout_seconds: int = 600):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def enrich(self, auction):
        schema = {
            "type": "object",
            "properties": {
                "summary_title": {"type": "string"},
                "summary_bullets": {"type": "array", "items": {"type": "string"}},
                "risk_label": {"type": "string"},
                "risk_comment": {"type": "string"},
                "mobile_highlights": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary_title", "summary_bullets", "risk_label", "risk_comment", "mobile_highlights"],
        }
        compact_payload = build_compact_auction_payload(auction)
        user_content = (
            "다음 경매 물건을 모바일 화면에서 바로 판단 보조로 볼 수 있게 한국어로 요약해줘.\n"
            "원문을 그대로 반복하지 말고, 확인 가능한 사실과 사람이 추가 확인해야 할 리스크를 분리해줘.\n"
            "risk_label은 low / review_recommended / high / unknown 중 하나로만 써줘.\n"
            "매각물건명세서에 없거나 불확실한 내용은 단정하지 말고 '확인 필요'로 표시해줘.\n\n"
            f"정제된 입력:\n{json.dumps(compact_payload, ensure_ascii=False)}"
        )
        payload = {
            "model": self.model_name,
            "stream": False,
            "format": schema,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "너는 법률 판단을 대신하지 않는 보수적인 한국 부동산 경매 검토 보조자다. "
                        "투자 권유나 법률 단정은 하지 말고, 매각물건명세서와 감정요약에서 확인 가능한 사실만 근거로 요약하라. "
                        "특히 지분매각, 특별매각조건, 공유자 우선매수권, 임차인/점유자, 대항력, 배당요구, 전유면적, 대지권, 회차별 최저가를 우선 확인하라. "
                        "불확실하거나 원문 근거가 부족하면 반드시 사람 검토 필요라고 적어라. "
                        "반복 양식 문구는 요약하지 말고 실제 물건 판단에 필요한 내용만 남겨라."
                    ),
                },
                {"role": "user", "content": user_content},
            ],
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        return json.loads(response.json()["message"]["content"])
