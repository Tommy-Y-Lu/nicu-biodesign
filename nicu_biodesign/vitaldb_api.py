from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen


Fetcher = Callable[[str], bytes]


def _default_fetcher(url: str) -> bytes:
    with urlopen(url, timeout=30) as response:
        return response.read()


@dataclass(frozen=True)
class VitalDBClient:
    base_url: str
    api_key: str | None = None
    fetcher: Fetcher = _default_fetcher

    def fetch_dataset(self, dataset_id: str, limit: int = 100) -> list[dict[str, Any]]:
        params = {"dataset": dataset_id, "limit": str(limit)}
        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{self.base_url.rstrip('/')}/records?{urlencode(params)}"
        payload = json.loads(self.fetcher(url).decode("utf-8"))
        records = payload.get("records") if isinstance(payload, dict) else None

        if not isinstance(records, list):
            raise ValueError("VitalDB API response must contain a 'records' list.")
        return records
