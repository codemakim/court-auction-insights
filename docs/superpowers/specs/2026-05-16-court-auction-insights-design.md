# Court Auction Insights Design

## Goal
Build a separate user-facing product that turns the crawler's raw auction data into mobile-friendly review cards, conservative AI summaries, and eventually conversational access, without making the crawler itself responsible for UI or LLM work.

## Project boundary
`court-auction-crawler` remains the data producer:
- discover auctions,
- download source documents,
- persist current auction state,
- persist historical snapshots,
- emit normalized change events.

`court-auction-insights` becomes the downstream consumer:
- read crawler-produced data,
- run local LLM enrichment one auction at a time,
- persist presentation-ready enrichment records,
- expose a web UI first and chat-style access later.

This should begin as a separate project that can read the crawler database directly. If the system later needs stronger isolation, the integration can evolve toward an API or event boundary without changing the product model.

## Product behavior
Each auction can appear in the UI even when no `매각물건명세서` has been uploaded yet.

### Auctions with no sale specification yet
- still appear in search/results/detail views,
- show normal non-document facts such as address, case number, current price, sale date, and status,
- display a clear badge such as `매각물건명세서 미업로드`,
- do **not** fabricate a document-based AI summary,
- remain eligible for later enrichment when the document appears.

### Auctions with an available sale specification
- show the same base auction facts,
- add an AI-generated review card based on the latest extracted document text,
- expose a conservative risk label and short explanation,
- surface when a summary became stale because a material fact or document changed.

## Why separate projects
The crawler and the insights product optimize for different things:
- the crawler needs reliability, idempotency, and low operational surprise,
- the insights product needs iteration speed, ranking logic, human-friendly presentation, and LLM orchestration.

Keeping them separate avoids turning the crawler into a mixed-purpose service that performs collection, inference, and presentation at once.

## Recommended first architecture
```text
court-auction-crawler
  auctions / snapshots / documents / document_texts / change_events
            |
            | shared database initially
            v
court-auction-insights
  enrichment queue -> sequential Ollama worker -> enrichment records -> web UI
```

### 1. Data ingestion boundary
The insights project reads the crawler database as a source of truth. Initial reads can be direct SQLite access against the crawler DB path configured by environment variable. The crawler remains the only writer for crawler-owned tables.

### 2. Local enrichment worker
The first worker processes exactly one eligible auction at a time:
1. find one auction with extracted `sale_spec` text and no current successful enrichment,
2. build a bounded prompt from normalized auction facts and extracted document text,
3. request structured JSON from Ollama,
4. validate the response,
5. persist an enrichment record,
6. move to the next auction.

The initial target model is configurable, with `gemma4:26b` as the first deployment choice. Ollama supports structured JSON responses and JSON-schema-constrained outputs, which fits this use case well. 

### 3. Enrichment staleness
An enrichment becomes stale when any of the following changes:
- the latest relevant auction snapshot hash,
- the linked `sale_spec` content hash,
- the enrichment prompt version,
- the enrichment output schema version.

The crawler's change events provide an additional useful signal for explaining *why* a previously viewed auction deserves renewed attention.

### 4. Web UI first, chat later
The first user-facing interface should be a responsive web UI rather than chat:
- list view for quickly scanning auctions,
- detail view for source facts, AI summary, change timeline, and document availability,
- mobile-first review cards for quick triage.

A chat interface can come later, once there are stored enrichments and change events worth querying conversationally. That keeps the first release concrete and reviewable instead of hiding the product behind open-ended prompts.

The web server should listen only on localhost on the host machine, then be exposed privately through Tailscale Serve for access from trusted tailnet devices. Tailscale documents that Serve can route tailnet traffic to a local service and recommends localhost-only backends when using identity-aware proxying behavior. 

## Suggested data model owned by `court-auction-insights`
### `auction_enrichments`
- `id`
- `auction_id`
- `source_snapshot_id`
- `source_document_id`
- `model_name`
- `prompt_version`
- `schema_version`
- `status` (`pending`, `success`, `failed`, `stale`, `waiting_for_source_document`)
- `summary_title`
- `summary_bullets_json`
- `risk_label`
- `risk_comment`
- `mobile_card_json`
- `source_hash`
- `generated_at`
- `error_message`

### Optional later tables
- `review_flags` for human notes such as `watch`, `dismiss`, or `needs_manual_review`
- `saved_filters` for recurring searches
- `chat_threads` and `chat_messages` only after the base UI is useful

## Status model for missing documents
A missing sale specification is not an error condition.

Recommended source-document states:
- `not_uploaded`
- `downloaded`
- `extraction_failed`

Recommended enrichment states:
- `waiting_for_source_document`
- `pending`
- `success`
- `failed`
- `stale`

This distinction matters because `not_uploaded` should show as an informative badge in the UI, while `extraction_failed` deserves operational attention.

## Risk posture
The model must not decide whether to bid. It should:
- summarize source material,
- highlight ambiguity,
- conservatively escalate uncertain cases,
- explain why a human should review something.

Example labels:
- `low_signal`
- `review_recommended`
- `manual_review_required`

The UI should state that summaries are assistive and not legal advice.

## First release scope
### Include
- separate project skeleton,
- configuration for crawler DB path and Ollama endpoint,
- direct read integration with crawler tables,
- enrichment table and migration setup,
- sequential one-by-one enrichment worker,
- list/detail web UI,
- clear `매각물건명세서 미업로드` badge behavior,
- stale-summary handling,
- basic mobile layout.

### Exclude for now
- public internet exposure,
- automatic bidding recommendations,
- multi-user accounts,
- real-time chat,
- embedding search / RAG,
- complex alerting rules.

## Operational shape
- Run the worker as a separate process from the web app.
- Keep both independently restartable.
- Prefer local-only service binding plus private Tailscale access for the UI.
- Store generated summaries so page views never need to synchronously call the model.

## Testing strategy
- contract tests against a copied/sample crawler database,
- worker tests for eligibility, staleness, JSON validation, and retry handling,
- UI tests for document badge states and stale-summary rendering,
- one integration test using a mocked Ollama response.

## Evolution path
### Phase 1
Standalone insights project, shared SQLite reads, sequential enrichment worker, responsive UI.

### Phase 2
Review workflow, filters, richer change timelines, manual notes.

### Phase 3
Chat over stored auction/enrichment/change-event data, and if needed, a cleaner API/event boundary between crawler and insights.
