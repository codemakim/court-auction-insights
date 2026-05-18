# Browse and Filter UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the insights app useful for day-to-day auction browsing with search, filters, sorting, enrichment-state badges, and a detail page.

**Architecture:** Extend the existing FastAPI JSON API with server-side filtering/sorting over crawler records plus enrichment presence. Split the React app into small files for API access, reusable UI, list page, and detail page so the current single-file component does not keep growing.

**Tech Stack:** FastAPI, SQLite, React, TypeScript, Vite, TanStack Query

---

## File structure
- `src/court_auction_insights/crawler_source.py`: derive district and support sorted base auction reads.
- `src/court_auction_insights/web.py`: parse API query parameters and serialize district / enrichment state.
- `tests/test_crawler_source.py`: backend adapter coverage.
- `tests/test_web.py`: API filtering / detail coverage.
- `frontend/src/types.ts`: shared frontend response types.
- `frontend/src/api.ts`: list/detail fetchers and query serialization.
- `frontend/src/components/AuctionCard.tsx`: reusable list card.
- `frontend/src/components/Filters.tsx`: browse controls.
- `frontend/src/pages/AuctionListPage.tsx`: list state and results.
- `frontend/src/pages/AuctionDetailPage.tsx`: detail view.
- `frontend/src/App.tsx`: tiny route switcher.
- `frontend/src/App.css`: shared styles for list/detail/filter UI.

### Task 1: Add district derivation and useful ordering
**Files:**
- Modify: `src/court_auction_insights/models.py`
- Modify: `src/court_auction_insights/crawler_source.py`
- Modify: `tests/test_crawler_source.py`

- [ ] Write failing tests asserting district extraction from Seoul addresses and newest-first ordering by `last_seen_at`.
- [ ] Run `pytest tests/test_crawler_source.py -q` and confirm the new tests fail for missing district / old ordering.
- [ ] Add a `district` field to `AuctionSourceRecord`, derive it from address text, and sort crawler rows by `a.last_seen_at DESC, a.id DESC`.
- [ ] Re-run `pytest tests/test_crawler_source.py -q` and confirm pass.
- [ ] Commit `feat: derive auction district and order latest first`.

### Task 2: Add list filtering and enrichment-state API support
**Files:**
- Modify: `src/court_auction_insights/web.py`
- Modify: `tests/test_web.py`

- [ ] Write failing API tests for `q`, `district`, `subtype`, min/max price, sale-spec status, enrichment status, and sort modes.
- [ ] Run `pytest tests/test_web.py -q` and confirm failures.
- [ ] Implement filter helpers in `web.py`, serialize `district`, and expose `enrichment_status` as `pending` or `completed`.
- [ ] Re-run `pytest tests/test_web.py -q` and confirm pass.
- [ ] Commit `feat: add browse filters to auction api`.

### Task 3: Split the React app and add browse controls
**Files:**
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`
- Create: `frontend/src/components/AuctionCard.tsx`
- Create: `frontend/src/components/Filters.tsx`
- Create: `frontend/src/pages/AuctionListPage.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/App.css`

- [ ] Extract current inline types and fetcher into dedicated files.
- [ ] Add browse controls for search, district, subtype, min/max price, sale-spec status, enrichment status, and sort.
- [ ] Render `AI 요약 전` when no enrichment exists and `AI 요약 완료` when it does.
- [ ] Run `npm run build` in `frontend/` and confirm pass.
- [ ] Commit `feat: add searchable auction browse page`.

### Task 4: Add React detail page
**Files:**
- Create: `frontend/src/pages/AuctionDetailPage.tsx`
- Modify: `frontend/src/api.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/AuctionCard.tsx`
- Modify: `frontend/src/App.css`

- [ ] Add detail fetcher and route selection from location path.
- [ ] Link each list card to `/auctions/:id`.
- [ ] Render gallery, identifiers, sale facts, sale-spec state, and AI section with either summary content or `AI 요약 전` placeholder.
- [ ] Run `npm run build` in `frontend/` and confirm pass.
- [ ] Commit `feat: add auction detail page`.

### Task 5: Verify end-to-end behavior and document next data work
**Files:**
- Modify: `README.md`
- Create or modify: `docs/superpowers/specs/2026-05-18-area-and-failed-count-follow-up.md`

- [ ] Run backend test suite with `pytest -q`.
- [ ] Run frontend build with `npm run build`.
- [ ] Manually verify list filters, newest-first ordering, card badges, and detail navigation in the browser.
- [ ] Add a short README section describing available filters.
- [ ] Add follow-up note that failed count needs parser completion and area filtering needs explicit semantics.
- [ ] Commit `docs: describe browse filters and next data work`.
