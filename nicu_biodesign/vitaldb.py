from __future__ import annotations

import csv
import gzip
import io
from dataclasses import dataclass
from typing import Any, Callable
from urllib.request import Request, urlopen


Fetcher = Callable[[str], bytes]

VALID_DATASETS = {"cases", "trks", "labs"}


def _default_fetcher(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "nicu-biodesign/0.1",
            "Accept": "text/csv, */*",
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read()


def _parse_csv(data: bytes) -> list[dict[str, Any]]:
    # VitalDB's open-data endpoints return gzip-compressed CSV.
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)

    text = data.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


@dataclass(frozen=True)
class VitalDBClient:
    base_url: str = "https://api.vitaldb.net"
    api_key: str | None = None
    fetcher: Fetcher = _default_fetcher

    def fetch_dataset(
        self,
        dataset_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch a limited number of rows from a VitalDB dataset.

        dataset_id must be one of: cases, trks, labs.
        The limit is applied locally after downloading the CSV.
        """
        if dataset_id not in VALID_DATASETS:
            raise ValueError(
                f"Unsupported dataset '{dataset_id}'. "
                f"Choose one of: {', '.join(sorted(VALID_DATASETS))}."
            )

        if limit < 0:
            raise ValueError("limit must be non-negative.")

        url = f"{self.base_url.rstrip('/')}/{dataset_id}"
        records = _parse_csv(self.fetcher(url))
        return records[:limit]

    def fetch_track(self, tid: str) -> list[dict[str, Any]]:
        """Fetch time/value records for a track ID from the track list."""
        if not tid or "/" in tid or "?" in tid or "#" in tid:
            raise ValueError("tid must be a valid track identifier.")

        url = f"{self.base_url.rstrip('/')}/{tid}"
        return _parse_csv(self.fetcher(url))