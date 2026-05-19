from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INSIGHTS_", env_file=".env", extra="ignore")

    crawler_db_path: Path
    crawler_image_root: Path = Path("/var/lib/court-auction-collector/data/images")
    db_path: Path
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma4:26b"
    ollama_timeout_seconds: int = 600
    worker_interval_seconds: int = 60
    web_host: str = "127.0.0.1"
    web_port: int = 8787
    prompt_version: str = "v3"
    schema_version: str = "v1"
