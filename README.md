# court-auction-insights

별도 수집기인 `court-auction-crawler`가 만든 데이터를 읽어, 로컬 LLM 요약과 모바일 친화 UI를 제공하는 프로젝트입니다.

## 설정

배포마다 바뀌는 값은 `.env`에 둡니다. 저장소에는 `.env.example`만 커밋합니다.

```bash
cp .env.example .env
```

기본 환경 변수:

- `INSIGHTS_CRAWLER_DB_PATH`: crawler가 소유한 SQLite DB 절대경로
- `INSIGHTS_DB_PATH`: insights가 소유한 SQLite DB 절대경로
- `INSIGHTS_OLLAMA_BASE_URL`: Ollama API 주소
- `INSIGHTS_OLLAMA_MODEL`: enrichment worker가 사용할 모델
- `INSIGHTS_WEB_HOST`, `INSIGHTS_WEB_PORT`: 로컬 웹 UI 바인딩 주소
- `INSIGHTS_PROMPT_VERSION`, `INSIGHTS_SCHEMA_VERSION`: 변경 시 기존 요약을 stale 처리하기 위한 버전 키

## 실행

```bash
python3.14 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
court-auction-insights init-db
court-auction-insights worker-once
court-auction-insights serve
```

웹 UI는 기본적으로 `127.0.0.1:8787`에만 바인딩됩니다. 외부에서 볼 필요가 생기면 별도 공개 포트 대신 사설 네트워크 프록시 계층을 두는 구성을 권장합니다.
