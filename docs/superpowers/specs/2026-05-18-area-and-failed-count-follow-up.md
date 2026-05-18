# Area and Failed-Count Follow-up

## Why this is separate
The browse UI can already support useful structured filters, but two requested dimensions need cleaner source data before they become dependable product controls.

## Failed auction count
The crawler schema already contains `failed_auction_count`, but current live records are not populated reliably. Before exposing it as a primary filter, inspect the live detail/list page source field, add parser coverage, and verify repeated collections update the value correctly across snapshots.

## Area
Area should not be shipped as one ambiguous number. Product semantics should be explicit:
- apartment / multi-unit housing: prefer exclusive area when available
- detached / multi-family: decide whether the product should expose building total area, land area, or both with different labels
- mixed-use cases: avoid collapsing several incompatible measurements into one sort key

## Recommended next increment
1. add a small live-data research task for the exact failed-count source field
2. add parser tests and populate `failed_auction_count`
3. inventory area expressions from sale-spec and appraisal text
4. choose named fields before adding UI filters
