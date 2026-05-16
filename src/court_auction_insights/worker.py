from dataclasses import dataclass
from pathlib import Path

from .db import get_latest_enrichment, save_enrichment


@dataclass(frozen=True)
class WorkerResult:
    auction_id: int | None
    status: str


class EnrichmentWorker:
    def __init__(
        self,
        crawler_source,
        db_path: Path,
        ollama_client,
        *,
        model_name: str = "gemma4:26b",
        prompt_version: str = "v1",
        schema_version: str = "v1",
    ):
        self.crawler_source = crawler_source
        self.db_path = Path(db_path)
        self.ollama_client = ollama_client
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.schema_version = schema_version

    def run_once(self) -> WorkerResult:
        for auction in self.crawler_source.list_auctions():
            if get_latest_enrichment(self.db_path, auction.id) is not None:
                continue
            if auction.sale_spec_status != "downloaded":
                save_enrichment(
                    self.db_path,
                    auction_id=auction.id,
                    source_document_id=auction.sale_spec_document_id,
                    model_name=self.model_name,
                    prompt_version=self.prompt_version,
                    schema_version=self.schema_version,
                    status="waiting_for_source_document",
                    source_hash=auction.sale_spec_content_hash,
                )
                return WorkerResult(auction.id, "waiting_for_source_document")

            payload = self.ollama_client.enrich(auction)
            save_enrichment(
                self.db_path,
                auction_id=auction.id,
                source_document_id=auction.sale_spec_document_id,
                model_name=self.model_name,
                prompt_version=self.prompt_version,
                schema_version=self.schema_version,
                status="success",
                source_hash=auction.sale_spec_content_hash,
                summary_title=payload["summary_title"],
                summary_bullets=payload["summary_bullets"],
                risk_label=payload["risk_label"],
                risk_comment=payload["risk_comment"],
                mobile_card={"highlights": payload.get("mobile_highlights", [])},
            )
            return WorkerResult(auction.id, "success")
        return WorkerResult(None, "idle")
