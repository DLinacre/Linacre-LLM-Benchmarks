"""Main orchestrator for the Linacre LLM Hub verified data engine."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from .adapters import (
    fetch_artificial_analysis_benchmarks,
    fetch_github_releases,
    fetch_github_trending_repos,
    fetch_huggingface_local_models,
    fetch_openrouter_models,
    static_source_transparency_entries,
)
from .schema import load_json_if_exists, save_json_atomic, utc_now_iso, wrap_envelope

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("linacre.data_engine.run")

ROOT_DIR = Path(__file__).resolve().parents[2]
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"
HISTORY_DIR = ROOT_DIR / "data" / "history"


def _preserve_or_update(
    target_path: Path,
    dataset_name: str,
    new_records: Any,
    has_data: bool,
    retrieved_at: str,
    source_meta: Dict[str, Any],
) -> Dict[str, Any]:
    """Never overwrite verified last-known-good data with an empty failed response."""
    existing = load_json_if_exists(target_path)
    if not has_data and existing and existing.get("data"):
        logger.warning("Preserving last-known-good data for %s (from %s)", dataset_name, existing.get("retrieved_at"))
        source_meta = dict(source_meta)
        source_meta["stale_fallback_used"] = True
        source_meta["last_successful_retrieval"] = existing.get("retrieved_at")
        return source_meta

    envelope = wrap_envelope(
        dataset=dataset_name,
        records=new_records,
        retrieved_at=retrieved_at,
        source_summary={
            "source_id": source_meta.get("id"),
            "source_name": source_meta.get("name"),
            "status": source_meta.get("status"),
        },
    )
    save_json_atomic(target_path, envelope)
    return source_meta


def run_all() -> int:
    now = utc_now_iso()
    sources_report: List[Dict[str, Any]] = []

    # 1. GitHub Trending AI Repositories
    repos, gh_repos_status = fetch_github_trending_repos()
    gh_repos_status = _preserve_or_update(
        PUBLIC_DATA_DIR / "trending_repos.json",
        "trending_repos",
        repos,
        len(repos) > 0,
        now,
        gh_repos_status,
    )
    sources_report.append(gh_repos_status)

    # 2. GitHub AI Releases (News & Releases)
    releases, gh_rel_status = fetch_github_releases()
    gh_rel_status = _preserve_or_update(
        PUBLIC_DATA_DIR / "releases.json",
        "releases",
        releases,
        len(releases) > 0,
        now,
        gh_rel_status,
    )
    sources_report.append(gh_rel_status)

    # 3. OpenRouter Model Catalogue & Pricing
    or_models, or_status = fetch_openrouter_models()
    or_status = _preserve_or_update(
        PUBLIC_DATA_DIR / "catalog.json",
        "catalog",
        or_models,
        len(or_models) > 0,
        now,
        or_status,
    )
    sources_report.append(or_status)

    # 4. Hugging Face Open-Weight / GGUF Models
    hf_models, hf_status = fetch_huggingface_local_models()
    hf_status = _preserve_or_update(
        PUBLIC_DATA_DIR / "local_models.json",
        "local_models",
        hf_models,
        len(hf_models) > 0,
        now,
        hf_status,
    )
    sources_report.append(hf_status)

    # 5. Artificial Analysis Leaderboards (optional API key)
    aa_boards, aa_status = fetch_artificial_analysis_benchmarks()
    has_aa = any(len(v) > 0 for v in aa_boards.values())
    leaderboards_payload = {
        "methodology_notice": "Each leaderboard uses an independent methodology and score scale. Scores from different leaderboards must not be merged or directly compared.",
        "categories": {
            "intelligence_index": {
                "title": "Intelligence Index",
                "methodology": "Artificial Analysis Intelligence Index (composite across reasoning, knowledge, and coding evaluations).",
                "source_name": "Artificial Analysis API v2",
                "source_url": "https://artificialanalysis.ai/",
                "unit": "index (0-100)",
                "entries": aa_boards.get("intelligence_index", []),
            },
            "coding_index": {
                "title": "Coding Benchmarks",
                "methodology": "Artificial Analysis Coding Index.",
                "source_name": "Artificial Analysis API v2",
                "source_url": "https://artificialanalysis.ai/",
                "unit": "index (0-100)",
                "entries": aa_boards.get("coding_index", []),
            },
            "math_index": {
                "title": "Mathematics Benchmarks",
                "methodology": "Artificial Analysis Math Index.",
                "source_name": "Artificial Analysis API v2",
                "source_url": "https://artificialanalysis.ai/",
                "unit": "index (0-100)",
                "entries": aa_boards.get("math_index", []),
            },
            "output_speed": {
                "title": "Model Output Speed",
                "methodology": "Median output generation speed measured in tokens per second.",
                "source_name": "Artificial Analysis API v2",
                "source_url": "https://artificialanalysis.ai/",
                "unit": "tokens/sec",
                "entries": aa_boards.get("output_speed", []),
            },
        },
    }
    aa_status = _preserve_or_update(
        PUBLIC_DATA_DIR / "leaderboards.json",
        "leaderboards",
        leaderboards_payload,
        has_aa,
        now,
        aa_status,
    )
    sources_report.append(aa_status)

    # 6. Static / User-Configured Sources Transparency
    sources_report.extend(static_source_transparency_entries())

    # Write sources health & transparency manifest
    sources_envelope = wrap_envelope(
        dataset="sources",
        records=sources_report,
        retrieved_at=now,
        source_summary={"total_sources": len(sources_report)},
    )
    save_json_atomic(PUBLIC_DATA_DIR / "sources.json", sources_envelope)

    # Write daily historical snapshot (summary only, compact)
    date_slug = now[:10]
    snapshot = {
        "schema_version": sources_envelope["schema_version"],
        "captured_at": now,
        "counts": {
            "trending_repos": len(repos),
            "releases": len(releases),
            "catalog_models": len(or_models),
            "local_models": len(hf_models),
        },
        "source_statuses": {s["id"]: s["status"] for s in sources_report},
    }
    save_json_atomic(HISTORY_DIR / f"{date_slug}.json", snapshot)

    logger.info("Data engine run complete. Sources processed: %d", len(sources_report))
    return 0


if __name__ == "__main__":
    sys.exit(run_all())
