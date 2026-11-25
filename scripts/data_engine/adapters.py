"""Official API adapters for Linacre LLM Hub.

Every adapter:
- Uses only documented, legitimate official endpoints.
- Never invents scores, pricing, or repository metrics.
- Returns structured status + provenance metadata so the UI can honestly
  display 'No Data Available' or 'Not Configured' when appropriate.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from .http_client import HttpFetchError, fetch_json
from .schema import deduplicate_by_key, utc_now_iso, validate_provenance_record

logger = logging.getLogger("linacre.data_engine.adapters")

CURATED_AI_REPOS = [
    ("ollama/ollama", "Local AI Runtime"),
    ("ggml-org/llama.cpp", "Local AI Runtime"),
    ("vllm-project/vllm", "Inference Engine"),
    ("huggingface/transformers", "Model Framework"),
    ("open-webui/open-webui", "Local AI UI"),
    ("langchain-ai/langchain", "Agent Framework"),
    ("microsoft/autogen", "Agent Framework"),
    ("crewAIInc/crewAI", "Agent Framework"),
    ("BerriAI/litellm", "Developer Tool"),
    ("lm-sys/FastChat", "Evaluation & Serving"),
    ("ggerganov/whisper.cpp", "Local AI Runtime"),
    ("comfyanonymous/ComfyUI", "Multimodal Tool"),
]


def _github_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_github_trending_repos() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch verified metadata for key open-source AI repositories from GitHub REST API."""
    now = utc_now_iso()
    headers = _github_headers()
    repos: List[Dict[str, Any]] = []
    errors: List[str] = []
    rate_remaining: Optional[str] = None

    for full_name, category in CURATED_AI_REPOS:
        url = f"https://api.github.com/repos/{full_name}"
        try:
            payload, resp_headers = fetch_json(url, headers=headers)
            rate_remaining = resp_headers.get("x-ratelimit-remaining", rate_remaining)
            license_info = payload.get("license") or {}
            record = {
                "source_id": f"github:{payload['full_name']}",
                "repo_name": payload["full_name"],
                "name": payload["name"],
                "owner": payload["owner"]["login"],
                "category": category,
                "description": payload.get("description") or "No description provided.",
                "stars": payload.get("stargazers_count"),
                "forks": payload.get("forks_count"),
                "open_issues": payload.get("open_issues_count"),
                "language": payload.get("language") or "Not Specified",
                "license": license_info.get("spdx_id") or license_info.get("name") or "Not Specified",
                "updated_at": payload.get("pushed_at") or payload.get("updated_at"),
                "source_url": payload["html_url"],
                "source_name": "GitHub REST API",
                "retrieved_at": now,
                "verification_status": "verified",
            }
            ok, errs = validate_provenance_record(record, ["source_id", "repo_name", "source_url", "retrieved_at"])
            if ok:
                repos.append(record)
            else:
                errors.extend(errs)
        except HttpFetchError as exc:
            errors.append(f"{full_name}: {exc}")
            if exc.status_code == 403:
                break

    repos = deduplicate_by_key(repos, "source_id")
    repos.sort(key=lambda r: r.get("stars") or 0, reverse=True)

    status = {
        "id": "github_repos",
        "name": "GitHub REST API (Repositories)",
        "official_url": "https://docs.github.com/en/rest",
        "data_obtained": "Open-source AI repository stars, forks, primary language, license, and last push date.",
        "auth_required": "Optional (GITHUB_TOKEN increases rate limit from 60/hr to 5,000/hr)",
        "access_tier": "Free",
        "last_successful_retrieval": now if repos else None,
        "status": "healthy" if repos else "error",
        "record_count": len(repos),
        "rate_limit_info": f"Remaining: {rate_remaining}" if rate_remaining is not None else "60 req/hr unauthenticated; 5,000 req/hr authenticated",
        "limitations": "Curated set of prominent open-source AI repositories; does not fabricate trending growth velocity.",
        "errors": errors[:5],
    }
    return repos, status


def fetch_github_releases() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch official latest releases for major open-source AI projects from GitHub."""
    now = utc_now_iso()
    headers = _github_headers()
    releases: List[Dict[str, Any]] = []
    errors: List[str] = []

    for full_name, category in CURATED_AI_REPOS[:8]:
        url = f"https://api.github.com/repos/{full_name}/releases?per_page=2"
        try:
            payload, _ = fetch_json(url, headers=headers)
            if not isinstance(payload, list):
                continue
            for rel in payload:
                if rel.get("draft"):
                    continue
                body = (rel.get("body") or "").strip()
                summary = body.splitlines()[0][:240] if body else "Official release published on GitHub."
                record = {
                    "source_id": f"github-release:{full_name}:{rel.get('id')}",
                    "project": full_name,
                    "category": category,
                    "title": rel.get("name") or rel.get("tag_name") or full_name,
                    "tag": rel.get("tag_name"),
                    "prerelease": bool(rel.get("prerelease")),
                    "summary": summary,
                    "published_at": rel.get("published_at"),
                    "event_date": rel.get("created_at") or rel.get("published_at"),
                    "source_url": rel.get("html_url"),
                    "source_name": "GitHub Releases API",
                    "retrieved_at": now,
                    "verification_status": "verified",
                }
                ok, _ = validate_provenance_record(record, ["source_id", "title", "source_url", "retrieved_at"])
                if ok:
                    releases.append(record)
        except HttpFetchError as exc:
            errors.append(f"{full_name}: {exc}")
            if exc.status_code == 403:
                break

    releases = deduplicate_by_key(releases, "source_id")
    releases.sort(key=lambda r: r.get("published_at") or "", reverse=True)

    status = {
        "id": "github_releases",
        "name": "GitHub Releases API",
        "official_url": "https://docs.github.com/en/rest/releases/releases",
        "data_obtained": "Official AI project releases, version tags, publication dates, and release links.",
        "auth_required": "Optional (GITHUB_TOKEN recommended)",
        "access_tier": "Free",
        "last_successful_retrieval": now if releases else None,
        "status": "healthy" if releases else "error",
        "record_count": len(releases),
        "rate_limit_info": "Shares GitHub REST API quota",
        "limitations": "Covers tracked open-source AI repositories; separates release creation date from publication date.",
        "errors": errors[:5],
    }
    return releases, status


def _parse_price_per_million(raw_per_token: Any) -> Optional[float]:
    """Convert OpenRouter per-token USD string to USD per 1M tokens."""
    if raw_per_token is None:
        return None
    try:
        val = float(raw_per_token)
        if val < 0:
            return None
        return round(val * 1_000_000, 4)
    except (ValueError, TypeError):
        return None


def fetch_openrouter_models() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch official model catalogue and published pricing from OpenRouter."""
    now = utc_now_iso()
    url = "https://openrouter.ai/api/v1/models"
    models: List[Dict[str, Any]] = []
    error_msg: Optional[str] = None

    try:
        payload, _ = fetch_json(url)
        raw_list = payload.get("data", []) if isinstance(payload, dict) else []
        for item in raw_list:
            model_id = item.get("id")
            if not model_id:
                continue
            pricing = item.get("pricing") or {}
            input_pm = _parse_price_per_million(pricing.get("prompt"))
            output_pm = _parse_price_per_million(pricing.get("completion"))
            cached_pm = _parse_price_per_million(pricing.get("input_cache_read"))
            arch = item.get("architecture") or {}
            modalities = arch.get("input_modalities") or ([arch.get("modality")] if arch.get("modality") else [])
            creator = model_id.split("/")[0] if "/" in model_id else "Unknown"
            is_free_tier = (input_pm == 0.0 and output_pm == 0.0) if (input_pm is not None and output_pm is not None) else False

            record = {
                "source_id": f"openrouter:{model_id}",
                "model_id": model_id,
                "model_name": item.get("name") or model_id,
                "creator": creator,
                "provider": "OpenRouter",
                "context_length": item.get("context_length"),
                "input_price_per_1m": input_pm,
                "output_price_per_1m": output_pm,
                "cached_input_price_per_1m": cached_pm,
                "free_tier_available": is_free_tier,
                "modalities": modalities,
                "license": "See provider terms",
                "source_url": f"https://openrouter.ai/models/{model_id}",
                "source_name": "OpenRouter Models API",
                "retrieved_at": now,
                "evaluation_date": None,
                "methodology": "Published API catalogue & provider pricing",
                "verification_status": "verified",
            }
            ok, _ = validate_provenance_record(record, ["source_id", "model_id", "model_name", "source_url", "retrieved_at"])
            if ok:
                models.append(record)
        models = deduplicate_by_key(models, "source_id")
    except HttpFetchError as exc:
        error_msg = str(exc)
        logger.warning("OpenRouter fetch failed: %s", exc)

    status = {
        "id": "openrouter",
        "name": "OpenRouter Models API",
        "official_url": "https://openrouter.ai/docs/api-reference/list-available-models",
        "data_obtained": "Model names, context windows, supported modalities, and published input/output/cached pricing.",
        "auth_required": "No (public catalogue endpoint)",
        "access_tier": "Free",
        "last_successful_retrieval": now if models else None,
        "status": "healthy" if models else "unavailable",
        "record_count": len(models),
        "rate_limit_info": "Public GET endpoint; refreshed on scheduled workflow runs",
        "limitations": "Reflects OpenRouter routing prices, which may differ from direct first-party provider pricing.",
        "errors": [error_msg] if error_msg else [],
    }
    return models, status


def fetch_huggingface_local_models() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch verified open-weight / GGUF models from the official Hugging Face Hub API."""
    now = utc_now_iso()
    url = "https://huggingface.co/api/models?filter=gguf&sort=downloads&direction=-1&limit=40"
    models: List[Dict[str, Any]] = []
    error_msg: Optional[str] = None

    try:
        payload, _ = fetch_json(url)
        if isinstance(payload, list):
            for item in payload:
                repo_id = item.get("id") or item.get("modelId")
                if not repo_id:
                    continue
                tags = item.get("tags") or []
                license_tag = next((t.replace("license:", "") for t in tags if t.startswith("license:")), "Not Specified")
                creator = repo_id.split("/")[0] if "/" in repo_id else "Community"
                record = {
                    "source_id": f"huggingface:{repo_id}",
                    "model_id": repo_id,
                    "model_name": repo_id.split("/")[-1],
                    "creator": creator,
                    "format": "GGUF",
                    "downloads": item.get("downloads"),
                    "likes": item.get("likes"),
                    "license": license_tag,
                    "tags": tags[:10],
                    "last_modified": item.get("lastModified"),
                    "source_url": f"https://huggingface.co/{repo_id}",
                    "source_name": "Hugging Face Hub API",
                    "retrieved_at": now,
                    "verification_status": "verified",
                }
                ok, _ = validate_provenance_record(record, ["source_id", "model_id", "source_url", "retrieved_at"])
                if ok:
                    models.append(record)
        models = deduplicate_by_key(models, "source_id")
    except HttpFetchError as exc:
        error_msg = str(exc)
        logger.warning("Hugging Face fetch failed: %s", exc)

    status = {
        "id": "huggingface",
        "name": "Hugging Face Hub API",
        "official_url": "https://huggingface.co/docs/hub/api",
        "data_obtained": "Open-weight GGUF model repositories, creators, download counts, likes, tags, and licenses.",
        "auth_required": "No (public Hub API; optional HF_TOKEN for higher limits)",
        "access_tier": "Free",
        "last_successful_retrieval": now if models else None,
        "status": "healthy" if models else "unavailable",
        "record_count": len(models),
        "rate_limit_info": "Public Hub API rate limits apply",
        "limitations": "Open weights are not necessarily OSI open-source; always verify each model's license.",
        "errors": [error_msg] if error_msg else [],
    }
    return models, status


def fetch_artificial_analysis_benchmarks() -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any]]:
    """Fetch official benchmark indices from Artificial Analysis API v2 if API key is configured."""
    now = utc_now_iso()
    api_key = os.environ.get("ARTIFICIAL_ANALYSIS_API_KEY", "").strip()

    if not api_key:
        status = {
            "id": "artificial_analysis",
            "name": "Artificial Analysis API",
            "official_url": "https://artificialanalysis.ai/",
            "data_obtained": "Intelligence index, coding index, math index, output speed (tokens/sec), and latency.",
            "auth_required": "Yes (ARTIFICIAL_ANALYSIS_API_KEY secret)",
            "access_tier": "Free tier available with API key & attribution",
            "last_successful_retrieval": None,
            "status": "not_configured",
            "record_count": 0,
            "rate_limit_info": "Per Artificial Analysis API tier",
            "limitations": "Requires ARTIFICIAL_ANALYSIS_API_KEY in GitHub Actions secrets. No synthetic scores are substituted.",
            "errors": [],
        }
        return {}, status

    url = "https://artificialanalysis.ai/api/v2/data/llms/models"
    leaderboards: Dict[str, List[Dict[str, Any]]] = {
        "intelligence_index": [],
        "coding_index": [],
        "math_index": [],
        "output_speed": [],
    }
    error_msg: Optional[str] = None
    count = 0

    try:
        payload, _ = fetch_json(url, headers={"x-api-key": api_key})
        items = payload.get("data", []) if isinstance(payload, dict) else []
        for item in items:
            model_id = item.get("id") or item.get("slug") or item.get("name")
            if not model_id:
                continue
            evals = item.get("evaluations") or {}
            creator = (item.get("model_creator") or {}).get("name") or "Unknown"
            base = {
                "model_id": str(model_id),
                "model_name": item.get("name") or str(model_id),
                "creator": creator,
                "source_url": "https://artificialanalysis.ai/",
                "source_name": "Artificial Analysis API v2",
                "retrieved_at": now,
                "evaluation_date": None,
                "verification_status": "verified",
            }
            mappings = [
                ("intelligence_index", evals.get("artificial_analysis_intelligence_index"), "Artificial Analysis Intelligence Index", "index (0-100)"),
                ("coding_index", evals.get("artificial_analysis_coding_index"), "Artificial Analysis Coding Index", "index (0-100)"),
                ("math_index", evals.get("artificial_analysis_math_index"), "Artificial Analysis Math Index", "index (0-100)"),
                ("output_speed", item.get("median_output_tokens_per_second"), "Median Output Speed", "tokens/sec"),
            ]
            for board_key, score, bench_name, unit in mappings:
                if isinstance(score, (int, float)) and not isinstance(score, bool):
                    rec = {
                        **base,
                        "source_id": f"aa:{board_key}:{model_id}",
                        "benchmark_name": bench_name,
                        "score": round(float(score), 2),
                        "score_unit": unit,
                        "methodology": f"{bench_name} via Artificial Analysis official API",
                    }
                    leaderboards[board_key].append(rec)
                    count += 1
        for board_key in leaderboards:
            leaderboards[board_key].sort(key=lambda r: r["score"], reverse=True)
    except HttpFetchError as exc:
        error_msg = str(exc)
        logger.warning("Artificial Analysis fetch failed: %s", exc)

    status = {
        "id": "artificial_analysis",
        "name": "Artificial Analysis API",
        "official_url": "https://artificialanalysis.ai/",
        "data_obtained": "Intelligence index, coding index, math index, output speed (tokens/sec), and latency.",
        "auth_required": "Yes (ARTIFICIAL_ANALYSIS_API_KEY secret)",
        "access_tier": "Free tier available with API key & attribution",
        "last_successful_retrieval": now if count > 0 else None,
        "status": "healthy" if count > 0 else "error",
        "record_count": count,
        "rate_limit_info": "Per Artificial Analysis API tier",
        "limitations": "Requires attribution to Artificial Analysis. Different indices use distinct methodologies and must not be merged.",
        "errors": [error_msg] if error_msg else [],
    }
    return leaderboards, status


def static_source_transparency_entries() -> List[Dict[str, Any]]:
    """Document sources that require local user setup or do not offer an open automated API."""
    return [
        {
            "id": "ollama_local",
            "name": "Ollama Local API",
            "official_url": "https://docs.ollama.com/api",
            "data_obtained": "Locally installed Ollama models on the user's machine (/api/tags).",
            "auth_required": "User-configured local endpoint (e.g. http://127.0.0.1:11434)",
            "access_tier": "Free & Local",
            "last_successful_retrieval": None,
            "status": "user_configured",
            "record_count": 0,
            "rate_limit_info": "Localhost only",
            "limitations": "Never scanned automatically. Connects only when explicitly enabled by the user in Local AI Explorer.",
            "errors": [],
        },
        {
            "id": "lmarena",
            "name": "LMArena (Chatbot Arena)",
            "official_url": "https://arena.ai/",
            "data_obtained": "Human preference Elo rankings (not scraped).",
            "auth_required": "No official public REST API for automated ingestion",
            "access_tier": "Public web leaderboard",
            "last_successful_retrieval": None,
            "status": "not_configured",
            "record_count": 0,
            "rate_limit_info": "N/A",
            "limitations": "Linacre LLM Hub does not run unauthorized scrapers or fabricate Elo scores. View live human preference rankings directly on arena.ai.",
            "errors": [],
        },
        {
            "id": "mlcommons",
            "name": "MLCommons (MLPerf)",
            "official_url": "https://mlcommons.org/",
            "data_obtained": "Published hardware inference & training benchmark methodology.",
            "auth_required": "Published periodic CSV/web results",
            "access_tier": "Free (open published results)",
            "last_successful_retrieval": None,
            "status": "not_configured",
            "record_count": 0,
            "rate_limit_info": "Periodic release cycles",
            "limitations": "Hardware-specific results are not directly comparable to model quality benchmarks.",
            "errors": [],
        },
    ]
