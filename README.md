# court-auction-insights

`court-auction-insights` is a local-first review layer for Korean court-auction data.

It sits downstream of [`court-auction-crawler`](https://github.com/codemakim/court-auction-crawler): the crawler collects source facts, documents, and auction photos; this project turns that raw material into a faster human review experience with:

- a mobile-friendly auction browsing UI,
- ordered property-photo display,
- sale-spec availability awareness,
- one-auction-at-a-time local LLM enrichment,
- a path toward change timelines, review prioritization, and later conversational access.

The guiding idea is simple: **collect once, review better**. The crawler remains the reliable data producer; this app becomes the human-facing layer for deciding what deserves a closer look.

## Current status

This project is early but already has the core seams in place:

- FastAPI backend for crawler-data reads, media serving, and enrichment workflows
- React + Vite frontend for the product UI
- direct integration with crawler-owned SQLite data
- ordered auction-photo reads from crawler storage
- safe media serving restricted to a configured image root
- local Ollama enrichment worker scaffold
- explicit handling for auctions whose `매각물건명세서` has not been uploaded yet

The current UI is the first product shell, not the final design. It already shows real crawler data and photos, and is being evolved toward richer mobile cards, detail pages, change tracking, and AI-assisted triage.

## Architecture

```text
court-auction-crawler
  auctions / snapshots / documents / document_texts / auction_images
                    |
                    | shared crawler DB + image files
                    v
court-auction-insights
  FastAPI backend -> enrichment worker -> React frontend
```

### Responsibility split

| Project | Owns |
| --- | --- |
| `court-auction-crawler` | collection, source documents, source photos, historical snapshots |
| `court-auction-insights` | enrichment, review-oriented APIs, media presentation, user-facing UI |

This separation keeps scraping reliability and product iteration from getting tangled together.

## Product behavior

### When a sale specification exists

The app can enrich the auction with a compact review card based on the latest extracted `매각물건명세서` text.

### When a sale specification is not uploaded yet

The auction should still remain visible. The UI can show ordinary auction facts and photos, while marking the sale-spec section as unavailable instead of fabricating an AI summary.

### When photos exist

The app reads the crawler-owned ordered image set and shows a representative card image plus gallery-ready media routes.

## Stack

### Backend

- Python 3.14
- FastAPI
- SQLite
- Pydantic Settings
- Ollama HTTP API

### Frontend

- React
- TypeScript
- Vite
- TanStack Query

## Configuration

Deployment-specific values live in `.env`. The repository commits only `.env.example` files.

```bash
cp .env.example .env
```

Backend environment variables:

| Variable | Purpose |
| --- | --- |
| `INSIGHTS_CRAWLER_DB_PATH` | absolute path to the crawler-owned SQLite DB |
| `INSIGHTS_CRAWLER_IMAGE_ROOT` | trusted root containing crawler-owned image files |
| `INSIGHTS_DB_PATH` | absolute path to the insights-owned SQLite DB |
| `INSIGHTS_OLLAMA_BASE_URL` | Ollama API endpoint |
| `INSIGHTS_OLLAMA_MODEL` | local model used by the enrichment worker |
| `INSIGHTS_WEB_HOST` / `INSIGHTS_WEB_PORT` | FastAPI bind target |
| `INSIGHTS_PROMPT_VERSION` / `INSIGHTS_SCHEMA_VERSION` | version keys that intentionally stale prior enrichments |

Frontend environment variables:

```bash
cd frontend
cp .env.example .env
```

| Variable | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | optional API base override; leave blank in local dev so the Vite proxy handles `/api` and `/media` |

## Quick start

### 1. Backend setup

```bash
python3.14 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
court-auction-insights init-db
```

### 2. Start the backend

```bash
. .venv/bin/activate
court-auction-insights serve
```

Default backend address:

```text
http://127.0.0.1:8787
```

Useful API routes:

```text
GET /api/auctions
GET /api/auctions/{id}
GET /media/{auction_id}/{image_index}
```

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev -- --host 127.0.0.1
```

The Vite dev server will print its local URL, typically:

```text
http://127.0.0.1:5173
```

In local development, Vite proxies `/api` and `/media` requests to the FastAPI backend.

## Local LLM enrichment

Run one enrichment pass at a time:

```bash
. .venv/bin/activate
court-auction-insights worker-once
```

The initial worker is intentionally sequential:

1. find one eligible auction,
2. build a structured prompt,
3. call Ollama,
4. validate JSON output,
5. persist the result,
6. move on to the next auction on a later pass.

The first target model is configurable and defaults to `gemma4:26b`.

## Development commands

### Backend tests

```bash
. .venv/bin/activate
pytest -q
```

### Frontend build

```bash
cd frontend
npm run build
```

## Repository layout

```text
court-auction-insights/
  src/court_auction_insights/   # FastAPI backend, worker, DB adapters
  frontend/                     # React + Vite product UI
  tests/                        # backend tests
  docs/superpowers/             # design specs and implementation plans
```

## Current roadmap

Near-term work:

1. complete the React detail view and mobile card polish,
2. run real single-auction Ollama enrichment against collected sale-spec text,
3. surface review labels and explanations in the UI,
4. consume crawler change events for “what changed?” timelines,
5. add richer filters and saved review workflows.

Later possibilities:

- conversational browsing over stored enrichment results,
- human review flags and notes,
- daily digests or alerting for material auction changes,
- a cleaner API/event boundary if the crawler and insights app eventually need stronger isolation.

## Safety posture

This app is an assistive review tool, not a legal authority and not an automated bidding system. Local LLM output should summarize signals, preserve uncertainty, and escalate ambiguous cases for human review rather than pretending to make final decisions.
