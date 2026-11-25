import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.data_engine.adapters import (
    _parse_price_per_million,
    fetch_artificial_analysis_benchmarks,
    static_source_transparency_entries,
)
from scripts.data_engine.run import _preserve_or_update
from scripts.data_engine.schema import (
    deduplicate_by_key,
    load_json_if_exists,
    save_json_atomic,
    validate_provenance_record,
    wrap_envelope,
)


class TestDataEngine(unittest.TestCase):
    def test_provenance_validation_accepts_valid_record(self):
        rec = {
            "source_id": "github:ollama/ollama",
            "repo_name": "ollama/ollama",
            "source_url": "https://github.com/ollama/ollama",
            "retrieved_at": "2026-11-25T17:00:00Z",
            "score": 82.5,
        }
        ok, errs = validate_provenance_record(rec, ["source_id", "repo_name", "source_url", "retrieved_at"])
        self.assertTrue(ok)
        self.assertEqual(errs, [])

    def test_provenance_validation_rejects_invalid_score_and_url(self):
        rec = {
            "source_id": "bad:1",
            "source_url": "javascript:alert(1)",
            "retrieved_at": "2026-11-25T17:00:00Z",
            "score": True,
        }
        ok, errs = validate_provenance_record(rec, ["source_id", "repo_name", "source_url", "retrieved_at"])
        self.assertFalse(ok)
        self.assertGreaterEqual(len(errs), 3)

    def test_deduplicate_by_key(self):
        records = [
            {"source_id": "a", "val": 1},
            {"source_id": "b", "val": 2},
            {"source_id": "a", "val": 3},
        ]
        unique = deduplicate_by_key(records, "source_id")
        self.assertEqual([r["val"] for r in unique], [1, 2])

    def test_parse_price_per_million(self):
        self.assertEqual(_parse_price_per_million("0.0000015"), 1.5)
        self.assertEqual(_parse_price_per_million("0"), 0.0)
        self.assertIsNone(_parse_price_per_million("-1"))
        self.assertIsNone(_parse_price_per_million(None))

    def test_preserve_last_known_good_on_failed_fetch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "catalog.json"
            good_env = wrap_envelope("catalog", [{"model_id": "verified/model"}], "2026-11-24T00:00:00Z")
            save_json_atomic(target, good_env)

            meta = _preserve_or_update(
                target,
                "catalog",
                [],
                has_data=False,
                retrieved_at="2026-11-25T00:00:00Z",
                source_meta={"id": "openrouter", "name": "OpenRouter", "status": "unavailable"},
            )
            self.assertTrue(meta.get("stale_fallback_used"))
            self.assertEqual(meta.get("last_successful_retrieval"), "2026-11-24T00:00:00Z")
            preserved = load_json_if_exists(target)
            self.assertEqual(len(preserved["data"]), 1)

    def test_artificial_analysis_not_configured_without_key(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ARTIFICIAL_ANALYSIS_API_KEY", None)
            boards, status = fetch_artificial_analysis_benchmarks()
            self.assertEqual(boards, {})
            self.assertEqual(status["status"], "not_configured")
            self.assertEqual(status["record_count"], 0)

    def test_static_transparency_entries_present(self):
        entries = static_source_transparency_entries()
        ids = {e["id"] for e in entries}
        self.assertIn("ollama_local", ids)
        self.assertIn("lmarena", ids)
        self.assertIn("mlcommons", ids)


if __name__ == "__main__":
    unittest.main()
