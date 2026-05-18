# Court Auction Browse and Filter UI Design

## Goal
Turn the current proof-of-concept list page into a usable first-pass browsing tool for daily auction review.

## Scope
This increment covers the core reading flow:
- Browse auctions in a useful default order.
- Filter by district, building subtype, price range, sale-spec availability, and AI enrichment availability.
- Open a detail page for one auction.
- Show a clear "AI 요약 전" state until enrichment exists.

This increment does **not** implement RAG, natural-language search, or area-based filtering yet.

## Current Data Readiness
Already available from the crawler DB:
- `minimum_sale_price`
- `residential_subtype`
- `sale_spec_status`
- `address`
- enrichment presence via the insights DB

Derivable now:
- `district` from Korean addresses such as `서울특별시 관악구 ...`

Present in schema but not yet reliably populated:
- `failed_auction_count`

Not yet structured enough for product filters:
- area values such as exclusive area, building area, and land area

## Recommended Product Shape
### List page
The list page should default to newest-crawled-first so newly collected records visibly appear at the top. It should include:
- free-text search across address, case number, and external key
- district filter
- building subtype filter
- minimum-price range inputs
- sale-spec filter
- enrichment filter (`AI 요약 전`, `AI 요약 완료`)
- simple sort selector (`최근 수집순`, `최저가 낮은순`, `최저가 높은순`, `매각기일 빠른순`)

Each card should show:
- representative photo if available
- address
- minimum sale price
- sale date
- district / subtype badges where available
- sale-spec badge
- enrichment badge, including `AI 요약 전` when no summary exists

### Detail page
A detail page should show:
- image gallery
- address and case identifiers
- sale information
- district and subtype
- sale-spec state
- AI section that either renders enrichment or a clear pre-enrichment placeholder

## Backend Shape
The FastAPI list endpoint should accept query parameters instead of forcing the frontend to fetch everything and filter locally:
- `q`
- `district`
- `subtype`
- `min_price`
- `max_price`
- `sale_spec_status`
- `enrichment_status`
- `sort`

The crawler adapter should expose derived district data and order by `last_seen_at DESC, id DESC` by default. This keeps the frontend simple and keeps later pagination possible.

## Data Model Follow-up
### District
District should be stored as a derived field in the crawler-side projection or directly on the insights API record. For now, parsing from address is sufficient; later normalization can move into crawler persistence if needed.

### Failed auction count
The existing schema already has `failed_auction_count`; the immediate issue is parser completeness, not schema design. A later crawler increment should identify the source field on the live site and populate it reliably before exposing it as a primary UI filter.

### Area
Area filtering should wait until we intentionally choose product semantics:
- residential units: likely exclusive area first
- detached / multi-family buildings: likely building total area or land area, but not both under one ambiguous label

## RAG Decision
RAG is intentionally deferred. The current bottleneck is structured browsing, not document retrieval. RAG becomes worthwhile once the product needs cross-auction natural-language questions, semantic comparisons, or conversational retrieval over large historical text collections.

## Testing Strategy
- backend tests for filtering, district derivation, sorting, and detail serialization
- frontend component tests for list filtering state and enrichment badge rendering where practical
- manual browser verification for the full browse-to-detail flow
