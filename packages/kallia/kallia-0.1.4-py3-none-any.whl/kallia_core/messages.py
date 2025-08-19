import requests
import kallia_core.settings as Settings
from typing import Any, Dict, List, Optional


class Messages:
    @staticmethod
    def send(
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: int = 8192,
        stream: bool = False,
    ) -> Optional[str]:
        endpoint_url = f"{Settings.KALLIA_PROVIDER_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {Settings.KALLIA_PROVIDER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": Settings.KALLIA_PROVIDER_MODEL,
            "stream": stream,
        }
        response = requests.post(endpoint_url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
