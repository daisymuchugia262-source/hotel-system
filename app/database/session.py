"""
JSON file store — generic read/write helper for repositories.

Each collection lives in its own JSON file:
    {
        "next_id": 3,
        "items": [ {...}, {...} ]
    }

No imports from services/ or api/.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class JsonStore:
    """Persists collections to individual JSON files under a data directory."""

    def __init__(self, data_dir: Path | str | None = None) -> None:
        if data_dir is None:
            # default: <backend>/data/
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ---- internal ----
    def _path(self, collection: str) -> Path:
        return self.data_dir / f"{collection}.json"

    def _read_raw(self, collection: str) -> Dict[str, Any]:
        path = self._path(collection)
        if not path.exists():
            return {"next_id": 1, "items": []}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"next_id": 1, "items": []}

    def _write_raw(self, collection: str, data: Dict[str, Any]) -> None:
        path = self._path(collection)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)  # atomic on Windows and POSIX

    # ---- public API ----
    def all(self, collection: str) -> List[Dict[str, Any]]:
        return list(self._read_raw(collection)["items"])

    def get(self, collection: str, record_id: int) -> Dict[str, Any] | None:
        for rec in self._read_raw(collection)["items"]:
            if rec.get("id") == record_id:
                return dict(rec)
        return None

    def create(self, collection: str, record: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read_raw(collection)
        record = dict(record)
        record["id"] = data["next_id"]
        data["next_id"] += 1
        data["items"].append(record)
        self._write_raw(collection, data)
        return dict(record)

    def update(self, collection: str, record_id: int,
               updates: Dict[str, Any]) -> Dict[str, Any] | None:
        data = self._read_raw(collection)
        for i, rec in enumerate(data["items"]):
            if rec.get("id") == record_id:
                rec.update(updates)
                rec["id"] = record_id
                data["items"][i] = rec
                self._write_raw(collection, data)
                return dict(rec)
        return None

    def delete(self, collection: str, record_id: int) -> bool:
        data = self._read_raw(collection)
        before = len(data["items"])
        data["items"] = [r for r in data["items"] if r.get("id") != record_id]
        if len(data["items"]) == before:
            return False
        self._write_raw(collection, data)
        return True

    def find(self, collection: str, **filters) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for rec in self._read_raw(collection)["items"]:
            if all(rec.get(k) == v for k, v in filters.items()):
                results.append(dict(rec))
        return results
