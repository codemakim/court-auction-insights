# 2026-05-20 최신 명세서 텍스트 선택

## 증상
- 크롤러가 같은 문서에 대해 v1/v2/v3 document_text row를 누적 저장하면 인사이트 API가 오래된 markdown을 볼 수 있었다.

## 조치
- 인사이트의 crawler source 쿼리를 수정해 각 document별 가장 최신 `document_texts.id`만 조인하도록 했다.
- 회귀 테스트를 추가해 v1 이후 v3 row가 추가되면 API가 v3 markdown을 반환하는지 검증했다.

## 검증
- backend pytest 통과.
- frontend production build 통과.
