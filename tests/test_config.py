from pathlib import Path

from court_auction_insights.config import Settings


def test_settings_load_mutable_values_from_environment(monkeypatch):
    monkeypatch.setenv("INSIGHTS_CRAWLER_DB_PATH", "/tmp/crawler.db")
    monkeypatch.setenv("INSIGHTS_DB_PATH", "/tmp/insights.db")
    monkeypatch.setenv("INSIGHTS_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("INSIGHTS_OLLAMA_MODEL", "gemma4:26b")
    monkeypatch.setenv("INSIGHTS_WEB_HOST", "127.0.0.1")
    monkeypatch.setenv("INSIGHTS_WEB_PORT", "8787")

    settings = Settings(_env_file=None)

    assert settings.crawler_db_path == Path("/tmp/crawler.db")
    assert settings.db_path == Path("/tmp/insights.db")
    assert settings.ollama_model == "gemma4:26b"
    assert settings.web_port == 8787


def test_settings_load_crawler_image_root(monkeypatch):
    monkeypatch.setenv("INSIGHTS_CRAWLER_DB_PATH", "/tmp/crawler.db")
    monkeypatch.setenv("INSIGHTS_DB_PATH", "/tmp/insights.db")
    monkeypatch.setenv("INSIGHTS_CRAWLER_IMAGE_ROOT", "/tmp/images")
    settings = Settings(_env_file=None)
    assert settings.crawler_image_root == Path("/tmp/images")
