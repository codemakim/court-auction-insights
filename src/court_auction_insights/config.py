from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INSIGHTS_", env_file=".env", extra="ignore")

    crawler_db_path: Path
    db_path: Path
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma4:26b"
    web_host: str = "127.0.0.1"
    web_port: int = 8787
    prompt_version: str = "v1"
    schema_version: str = "v1"
