# React Frontend Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the insights product UI from temporary Jinja templates to a dedicated React frontend while keeping FastAPI as the data/worker backend.

**Architecture:** Add JSON API endpoints to FastAPI, scaffold a Vite React app in `frontend/`, consume crawler/enrichment/photo data through typed client calls, and make the React app the primary UI for mobile-first browsing.

**Tech Stack:** FastAPI, React, TypeScript, Vite, TanStack Query, Vitest, Playwright later

---

### Task 1: Backend API surface
- [ ] Add failing tests for JSON endpoints: `/api/auctions`, `/api/auctions/{id}`.
- [ ] Return photos, sale-spec status, and latest enrichment data in JSON.
- [ ] Verify backend tests pass.
- [ ] Commit.

### Task 2: Frontend project scaffold
- [ ] Create `frontend/` with Vite + React + TypeScript.
- [ ] Add env-backed API base URL contract.
- [ ] Add initial app shell and test setup.
- [ ] Commit.

### Task 3: Auction list UI
- [ ] Build mobile-first card list consuming `/api/auctions`.
- [ ] Show representative photo, address, status, price, and sale-spec badge.
- [ ] Add loading/empty states.
- [ ] Verify frontend tests/build.
- [ ] Commit.

### Task 4: Auction detail UI
- [ ] Build detail page consuming `/api/auctions/{id}`.
- [ ] Render gallery, source facts, enrichment summary, and document badge.
- [ ] Verify frontend tests/build.
- [ ] Commit.

### Task 5: Dev/runtime integration
- [ ] Add README instructions for starting backend and frontend together.
- [ ] Add CORS/dev-server config as needed.
- [ ] Verify browser flow against real local data.
- [ ] Commit.
