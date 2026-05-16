# Court Auction Insights Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first standalone `court-auction-insights` service that reads crawler data, enriches one auction at a time through Ollama, and serves a mobile-friendly web UI that clearly handles missing sale specifications.

**Architecture:** Keep the crawler and insights app as separate projects. The insights app reads crawler-owned SQLite data, stores its own enrichment state in its own SQLite database, runs a sequential worker process, and exposes a localhost-only web server that can later be shared privately through Tailscale Serve.

**Tech Stack:** Python 3.14, FastAPI, Jinja2, SQLite, SQLAlchemy, Pydantic Settings, Ollama HTTP API, pytest

---

## File structure

```text
court-auction-insights/
  .gitignore
  .env.example
  pyproject.toml
  README.md
  src/court_auction_insights/
    __init__.py
    config.py
    db.py
    crawler_source.py
    models.py
    enrichment.py
    worker.py
    web.py
    templates/
      base.html
      auctions.html
      auction_detail.html
    static/
      app.css
  tests/
    conftest.py
    test_config.py
    test_crawler_source.py
    test_enrichment.py
    test_worker.py
    test_web.py
```

## Environment contract

Use `.env` for mutable deployment values and keep only `.env.example` in git.

```dotenv
# Absolute path to the crawler-owned SQLite database.
INSIGHTS_CRAWLER_DB_PATH=/var/lib/court-auction-collector/data/court_auction.db

# Absolute path to the insights-owned SQLite database.
INSIGHTS_DB_PATH=/var/lib/court-auction-insights/data/insights.db

# Ollama API endpoint reachable from this host.
INSIGHTS_OLLAMA_BASE_URL=http://127.0.0.1:11434

# Local model used by the sequential enrichment worker.
INSIGHTS_OLLAMA_MODEL=gemma4:26b

# Local-only bind target for the web UI.
INSIGHTS_WEB_HOST=127.0.0.1
INSIGHTS_WEB_PORT=8787

# Version identifiers that intentionally stale prior enrichments when changed.
INSIGHTS_PROMPT_VERSION=v1
INSIGHTS_SCHEMA_VERSION=v1
```

### Task 1: Project bootstrap and settings

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/court_auction_insights/__init__.py`
- Create: `src/court_auction_insights/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing settings tests**

```python
from pathlib import Path

from court_auction_insights.config import Settings


def test_settings_load_mutable_values_from_environment(monkeypatch):
    monkeypatch.setenv("INSIGHTS_CRAWLER_DB_PATH", "/tmp/crawler.db")
    monkeypatch.setenv("INSIGHTS_DB_PATH", "/tmp/insights.db")
    monkeypatch.setenv("INSIGHTS_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("INSIGHTS_OLLAMA_MODEL", "gemma4:26b")
    monkeypatch.setenv("INSIGHTS_WEB_HOST", "127.0.0.1")
    monkeypatch.setenv("INSIGHTS_WEB_PORT", "8787")

    settings = Settings()

    assert settings.crawler_db_path == Path("/tmp/crawler.db")
    assert settings.db_path == Path("/tmp/insights.db")
    assert settings.ollama_model == "gemma4:26b"
    assert settings.web_port == 8787
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `pytest tests/test_config.py -q`

Expected: FAIL because `court_auction_insights.config` does not exist yet.

- [ ] **Step 3: Add the minimal settings implementation and project metadata**

Implement `Settings` with `pydantic-settings`, add package metadata and dependencies, ignore `.env`, and document the env contract in `.env.example` and `README.md`.

- [ ] **Step 4: Run the settings test and verify it passes**

Run: `pytest tests/test_config.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitignore .env.example pyproject.toml README.md src/court_auction_insights tests/test_config.py
git commit -m "chore: bootstrap insights project settings"
```

### Task 2: Crawler read adapter and document status view

**Files:**
- Create: `src/court_auction_insights/crawler_source.py`
- Create: `src/court_auction_insights/models.py`
- Test: `tests/conftest.py`
- Test: `tests/test_crawler_source.py`

- [ ] **Step 1: Write failing tests for source reads**

Create a temporary crawler-style SQLite database fixture with minimal `auctions`, `documents`, and `document_texts` rows. Test that auctions with no sale spec are returned with `sale_spec_status == "not_uploaded"`, and auctions with extracted sale spec text are returned with `sale_spec_status == "downloaded"` plus markdown text.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_crawler_source.py -q`

Expected: FAIL because the adapter does not exist yet.

- [ ] **Step 3: Implement the minimal read adapter**

Expose:

```python
class CrawlerSource:
    def list_auctions(self) -> list[AuctionSourceRecord]: ...
    def get_auction(self, auction_id: int) -> AuctionSourceRecord | None: ...
```

Use read-only SQLite connections and derive `sale_spec_status` from document presence and extraction result.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `pytest tests/test_crawler_source.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/court_auction_insights/crawler_source.py src/court_auction_insights/models.py tests/conftest.py tests/test_crawler_source.py
git commit -m "feat: read crawler auction records"
```

### Task 3: Insights-owned enrichment persistence

**Files:**
- Create: `src/court_auction_insights/db.py`
- Extend: `src/court_auction_insights/models.py`
- Test: `tests/test_enrichment.py`

- [ ] **Step 1: Write failing tests for enrichment persistence and staleness**

Test that:
- a new enrichment row can be stored,
- `waiting_for_source_document` is valid,
- changing source hash marks the current enrichment stale.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_enrichment.py -q`

Expected: FAIL because persistence code does not exist yet.

- [ ] **Step 3: Implement the minimal database layer**

Create the `auction_enrichments` table and helpers:

```python
def init_db(path: Path) -> None: ...
def save_enrichment(...): ...
def get_latest_enrichment(...): ...
def mark_stale_if_source_changed(...): ...
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `pytest tests/test_enrichment.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/court_auction_insights/db.py src/court_auction_insights/models.py tests/test_enrichment.py
git commit -m "feat: persist auction enrichments"
```

### Task 4: Sequential Ollama enrichment worker

**Files:**
- Create: `src/court_auction_insights/enrichment.py`
- Create: `src/court_auction_insights/worker.py`
- Test: `tests/test_worker.py`

- [ ] **Step 1: Write failing worker tests**

Test that the worker:
- skips auctions with `sale_spec_status == "not_uploaded"` by saving `waiting_for_source_document`,
- enriches exactly one eligible auction per run,
- validates structured JSON output,
- stores model and version metadata.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_worker.py -q`

Expected: FAIL because worker code does not exist yet.

- [ ] **Step 3: Implement the minimal worker**

Add:

```python
class OllamaClient:
    def enrich(self, payload: PromptPayload) -> EnrichmentResponse: ...

class EnrichmentWorker:
    def run_once(self) -> WorkerResult: ...
```

Use a JSON-schema-constrained response contract and process one auction at a time.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `pytest tests/test_worker.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/court_auction_insights/enrichment.py src/court_auction_insights/worker.py tests/test_worker.py
git commit -m "feat: add sequential enrichment worker"
```

### Task 5: Web UI for list and detail screens

**Files:**
- Create: `src/court_auction_insights/web.py`
- Create: `src/court_auction_insights/templates/base.html`
- Create: `src/court_auction_insights/templates/auctions.html`
- Create: `src/court_auction_insights/templates/auction_detail.html`
- Create: `src/court_auction_insights/static/app.css`
- Test: `tests/test_web.py`

- [ ] **Step 1: Write failing web tests**

Test that:
- the list page renders auction cards,
- auctions without sale specs show `매각물건명세서 미업로드`,
- detail pages show AI summary fields when enrichment exists,
- stale enrichments are visibly labeled.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_web.py -q`

Expected: FAIL because the app does not exist yet.

- [ ] **Step 3: Implement the minimal FastAPI/Jinja app**

Render a responsive list/detail UI from crawler rows plus latest enrichment rows. Keep the server bind configurable through env-backed settings.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `pytest tests/test_web.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/court_auction_insights/web.py src/court_auction_insights/templates src/court_auction_insights/static tests/test_web.py
git commit -m "feat: add auction insights web ui"
```

### Task 6: CLI entry points and operator docs

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Create: `tests/test_cli_smoke.py`

- [ ] **Step 1: Write failing CLI smoke tests**

Test that installed console commands exist for:
- `court-auction-insights init-db`
- `court-auction-insights worker-once`
- `court-auction-insights serve`

- [ ] **Step 2: Run the tests and verify they fail**

Run: `pytest tests/test_cli_smoke.py -q`

Expected: FAIL because console scripts are not defined yet.

- [ ] **Step 3: Implement console commands and README instructions**

Document:
- copying `.env.example` to `.env`,
- choosing absolute DB paths,
- running the worker once,
- starting the localhost web server,
- optionally exposing it through Tailscale Serve later.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `pytest tests/test_cli_smoke.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md tests/test_cli_smoke.py src/court_auction_insights
git commit -m "feat: add cli entry points"
```

### Task 7: Full verification

**Files:**
- No new files required.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Review the README against the environment contract**

Confirm every mutable path/host/model value is represented in `.env.example` and documented.

- [ ] **Step 3: Commit any final documentation fixes**

```bash
git add .
git commit -m "docs: finalize insights setup guidance"
```
