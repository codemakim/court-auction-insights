import argparse
import json
import time

import uvicorn

from .config import Settings
from .crawler_source import CrawlerSource
from .db import init_db
from .enrichment import OllamaClient
from .web import create_app
from .worker import EnrichmentWorker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="court-auction-insights")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db")
    subparsers.add_parser("worker-once")
    worker_loop = subparsers.add_parser("worker-loop")
    worker_loop.add_argument("--interval-seconds", type=int, default=None)
    subparsers.add_parser("serve")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    if args.command == "init-db":
        init_db(settings.db_path)
        return
    if args.command in {"worker-once", "worker-loop"}:
        init_db(settings.db_path)
        client = OllamaClient(
            settings.ollama_base_url,
            settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
        worker = EnrichmentWorker(
            CrawlerSource(settings.crawler_db_path),
            settings.db_path,
            client,
            model_name=settings.ollama_model,
            prompt_version=settings.prompt_version,
            schema_version=settings.schema_version,
        )
        if args.command == "worker-once":
            print(json.dumps(worker.run_once().__dict__, ensure_ascii=False))
            return
        interval_seconds = args.interval_seconds or settings.worker_interval_seconds
        while True:
            print(json.dumps(worker.run_once().__dict__, ensure_ascii=False), flush=True)
            time.sleep(interval_seconds)
    app = create_app(settings.crawler_db_path, settings.db_path, settings.crawler_image_root)
    uvicorn.run(app, host=settings.web_host, port=settings.web_port)
