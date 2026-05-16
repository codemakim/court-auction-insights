from dataclasses import asdict
import json

import requests


class OllamaClient:
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def enrich(self, auction):
        schema = {
            "type": "object",
            "properties": {
                "summary_title": {"type": "string"},
                "summary_bullets": {"type": "array", "items": {"type": "string"}},
                "risk_label": {"type": "string"},
                "risk_comment": {"type": "string"},
                "mobile_highlights": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary_title", "summary_bullets", "risk_label", "risk_comment", "mobile_highlights"],
        }
        payload = {
            "model": self.model_name,
            "stream": False,
            "format": schema,
            "messages": [
                {
                    "role": "system",
                    "content": "너는 법률 판단을 대신하지 않는 보수적인 경매 검토 보조자다. 불확실하면 사람 검토를 권하라.",
                },
                {
                    "role": "user",
                    "content": f"다음 경매 물건을 한국어로 요약해줘.\n{asdict(auction)}",
                },
            ],
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        return json.loads(response.json()["message"]["content"])
