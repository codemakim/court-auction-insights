# Auction Derived Property Facts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surface immediately useful property facts from already-collected address/appraisal text without modifying the crawler.

**Architecture:** Add deterministic extractors in the insights source layer. Serialize derived fields through the existing FastAPI API and show them in the React list/detail UI. Keep uncertainty explicit by labeling values as parsed/reference data.

**Tech Stack:** Python, FastAPI, pytest, React/Vite/TypeScript.

---

## Scope

In scope:
- Parse district/neighborhood/building name/floor/unit from address where possible.
- Parse total floors and approval date from appraisal summary where possible.
- Keep `area_note` as a textual hint, not a normalized area field.
- Show derived property facts in list/detail UI.

Out of scope:
- Crawler changes.
- Auction event history extraction.
- Normalized exclusive/supply area columns.

## Tasks

1. Add tests for parsing address/property facts.
2. Implement source-layer extractors and dataclass fields.
3. Add API serialization fields and summary counts.
4. Render facts in list/detail UI.
5. Run pytest and frontend build.
6. Write work log, commit, push.
