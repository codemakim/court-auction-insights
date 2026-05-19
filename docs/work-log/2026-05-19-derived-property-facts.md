# 2026-05-19 경매 판단용 물건 실체 단서 추출

## 작업 내용
- 크롤러 수집 흐름은 건드리지 않고 인사이트 계층에서 이미 저장된 주소/감정평가요약을 구조화했다.
- 주소에서 동, 건물명, 층, 호를 추출했다.
- 감정평가요약에서 전체층과 사용승인일을 추출했다.
- API와 UI에 파생 필드를 노출했다.
- 목록 상단 summary에 “실체 단서” 수를 추가했다.

## 오류 증상
- 화면에 주소/가격은 있으나 실제 검토자가 궁금해하는 건물명, 층, 호, 사용승인일 같은 물건 실체 정보가 잘 드러나지 않았다.

## 원인
- crawler DB에는 원문 주소/감정요약만 있고, 인사이트 계층에서 판단용 파생 필드를 만들지 않았다.

## 조치
- `AuctionSourceRecord`에 다음 필드 추가:
  - `neighborhood`
  - `building_name`
  - `floor`
  - `unit`
  - `total_floors`
  - `approval_date`
- `CrawlerSource._extract_property_facts()` 추가.
- `/api/auctions`, `/api/auctions/{id}` 직렬화에 파생 필드 추가.
- `/api/summary`에 `derived_fact_count` 추가.
- 목록 카드와 상세 화면에 파생 필드 표시.

## 검증
- RED:
  - 파생 필드 부재 테스트 실패 확인.
- GREEN:
  - `pytest -q` → `30 passed in 0.58s`
  - `npm run build` → 성공.

## 결과/남은 확인
- 현재 저장된 데이터만으로도 건물명/층/호/사용승인일 단서를 볼 수 있다.
- 기일 이력 raw row는 현재 crawler DB에 저장되어 있지 않아 이번 범위에서 제외했다.
- 전용/공급면적 정규화는 별도 안전 작업으로 분리해야 한다.
