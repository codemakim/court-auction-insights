# 2026-05-19 수집 데이터 가시성 개선

## 작업 내용
- 크롤러 수집 로직은 건드리지 않고, 인사이트 API/UI만 개선했다.
- `/api/summary`를 추가해 현재 수집 데이터 현황을 한 번에 볼 수 있게 했다.
- 물건 API에 `sale_spec_markdown`, `discount_rate`, `price_gap`, `image_count`를 추가했다.
- 목록 상단에 수집 물건 수, 명세서 확보/대기 수, 사진 수, AI 요약 수를 표시했다.
- 목록 카드에 할인율과 사진 수를 표시했다.
- 상세 화면에 감정가 대비 차액과 매각물건명세서 markdown 원문이 있으면 표시하도록 했다.
- 지역/유형 필터 선택지는 현재 DB에 있는 값에서 동적으로 받도록 했다.

## 오류 증상
- 데이터는 쌓이고 있지만 화면에서 “무엇이 수집됐는지”, “판단에 바로 쓸 수 있는 값이 무엇인지”가 잘 드러나지 않았다.

## 원인
- API가 원천 필드 중심으로만 내려주고, 수집 현황/파생 판단값을 별도로 제공하지 않았다.
- UI 상단에 현재 데이터 상태 요약이 없었다.

## 조치
- `src/court_auction_insights/web.py`
  - `/api/summary` 추가.
  - 할인율, 감정가 대비 차액, 이미지 수, 명세서 markdown 직렬화 추가.
- `frontend/src/pages/AuctionListPage.tsx`
  - summary strip 추가.
- `frontend/src/components/AuctionCard.tsx`
  - 할인율/사진 수 표시.
- `frontend/src/pages/AuctionDetailPage.tsx`
  - 감정가 대비 차액 및 명세서 markdown 표시.
- `frontend/src/components/Filters.tsx`
  - district/subtype 옵션을 API summary 기반으로 변경.

## 검증
- API 테스트 추가 후 RED 확인.
- 구현 후 `pytest -q` → `24 passed in 0.55s`.
- frontend build → 성공.

## 결과/남은 확인
- 이제 수집 데이터가 쌓일수록 목록 상단에서 전체 상태를 볼 수 있다.
- 아직 핵심 가치는 매각물건명세서 텍스트와 AI 요약/리스크 분석이 붙어야 완성된다.
