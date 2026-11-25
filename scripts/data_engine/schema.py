"""Schema validation, provenance checks, duplicate detection, and safe persistence."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import SCHEMA_VERSION


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_provenance_record(record: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """Validate that a record contains required fields and valid provenance."""
    errors: List[str] = []
    for field in required_fields:
        val = record.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"Missing required field: {field}")

    source_url = record.get("source_url")
    if source_url and not (str(source_url).startswith("https://") or str(source_url).startswith("http://")):
        errors.append(f"Invalid source_url: {source_url}")

    if "score" in record and record["score"] is not None:
        if not isinstance(record["score"], (int, float)) or isinstance(record["score"], bool):
            errors.append(f"Invalid score type: {record['score']!r}")
        elif record["score"] != record["score"]:  # NaN check
            errors.append("Score is NaN")

    return len(errors) == 0, errors


def deduplicate_by_key(records: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """Remove duplicate records by a stable identifier while preserving order."""
    seen = set()
    unique: List[Dict[str, Any]] = []
    for item in records:
        val = item.get(key)
        if not val or val in seen:
            continue
        seen.add(val)
        unique.append(item)
    return unique


def load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def save_json_atomic(path: Path, payload: Dict[str, Any]) -> bool:
    """Write JSON atomically only if semantic content (excluding volatile metadata if unchanged) differs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
            if existing == serialized:
                return False
        except OSError:
            pass
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(serialized, encoding="utf-8")
    os.replace(tmp_path, path)
    return True


def wrap_envelope(
    dataset: str,
    records: Any,
    retrieved_at: str,
    source_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Wrap normalized records in a versioned, provenance-tracked envelope."""
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset": dataset,
        "retrieved_at": retrieved_at,
        "source_summary": source_summary or {},
        "data": records,
    }
