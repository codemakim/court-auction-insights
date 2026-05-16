# Auction Photo UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show crawler-collected auction photos in the insights list and detail UI without duplicating image files.

**Architecture:** Extend the crawler read adapter to include ordered `auction_images`, expose a safe image route that only serves files under `INSIGHTS_CRAWLER_IMAGE_ROOT`, and update templates so cards use one representative image while detail pages render the full gallery.

**Tech Stack:** Python 3.14, FastAPI, Jinja2, SQLite, pytest

---

### Task 1: Settings and source-model extension
- [ ] Add failing tests for `crawler_image_root` configuration and auction image reads.
- [ ] Extend settings and source records with ordered image metadata.
- [ ] Verify focused tests pass.
- [ ] Commit.

### Task 2: Safe image serving route
- [ ] Add failing tests for valid in-root files and blocked out-of-root files.
- [ ] Implement `/media/{auction_id}/{image_index}` route.
- [ ] Verify focused tests pass.
- [ ] Commit.

### Task 3: UI rendering
- [ ] Add failing UI tests for representative card image, no-photo placeholder, and detail gallery.
- [ ] Update templates and light CSS.
- [ ] Verify focused tests pass.
- [ ] Commit.

### Task 4: Verification
- [ ] Run the full test suite.
- [ ] Start the web app against the real crawler DB and visually inspect one auction with images.
- [ ] Commit any final docs if needed.
