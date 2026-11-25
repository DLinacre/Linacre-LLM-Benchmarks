# Linacre LLM Hub

**Verified AI Intelligence Workstation** — real benchmark provenance, published model pricing, local AI discovery, hardware compatibility estimation, and open-source AI project tracking across Web (GitHub Pages), Windows (Electron), and Android (Capacitor).

## Core Principle: Accuracy Above Everything

Linacre LLM Hub never fabricates benchmark scores, pricing, or repository metrics.

- **Real data only**: Every dataset is fetched from official APIs with full provenance (`source_id`, `source_url`, `source_name`, `retrieved_at`).
- **Honest unavailable states**: Missing data is labeled **No Data Available**; optional integrations without API keys are labeled **Not Configured**.
- **Independent methodologies**: Leaderboards from different evaluation methodologies are never merged into a single fabricated "overall" score.
- **Last-known-good preservation**: Failed refreshes never overwrite verified data with empty responses.

## Features

1. **AI Intelligence Dashboard** — Verified source health, top open-source AI repositories, latest official releases, and workspace summary.
2. **Global AI Leaderboards** — Independent, searchable leaderboards with methodology notices and source attribution (populated via Artificial Analysis API v2 when `ARTIFICIAL_ANALYSIS_API_KEY` is configured).
3. **Model Comparison** — Side-by-side comparison of context windows, input/output/cached pricing, modalities, licensing, and provider links.
4. **Hardware Compatibility Calculator** — Transparent VRAM, KV cache, runtime overhead, GPU/CPU offloading, and disk space estimator for GGUF, FP16, BF16, and EXL2 formats with disclosed assumptions.
5. **Local AI Explorer** — Hugging Face GGUF model discovery plus an explicit opt-in local Ollama connection (`/api/tags`, never scans networks automatically).
6. **AI Pricing Intelligence** — Published provider token pricing and an interactive token-cost calculator.
7. **Open-Source AI Projects** — Verified GitHub repository metrics (stars, forks, language, license, last push) with category, language, and sort filters.
8. **AI News & Releases** — Official AI software releases separating publication date from event date.
9. **Personal Workspace** — Local favourites, recently viewed items, saved hardware profiles, and JSON export (no account required).
10. **Data Sources & Transparency** — Live status, auth requirements, rate limits, retrieval timestamps, and known limitations for every provider.

## Data Providers

| Provider | Data Obtained | Auth Required | Tier |
| --- | --- | --- | --- |
| **GitHub REST API** | Open-source AI repos & official releases | Optional (`GITHUB_TOKEN`) | Free |
| **OpenRouter Models API** | Model catalogue, context windows, modalities, published pricing | None | Free |
| **Hugging Face Hub API** | Open-weight GGUF repositories, downloads, licenses | None | Free |
| **Artificial Analysis API v2** | Intelligence, coding, math indices & output speed | Yes (`ARTIFICIAL_ANALYSIS_API_KEY`) | Free tier with key & attribution |
| **Ollama Local API** | Locally installed models (`/api/tags`) | User-configured local URL | Free & Local |
| **LMArena / MLCommons** | Documented transparently; not scraped | N/A | Public web / periodic |

## Local Development

Requires **Node.js 22+** and **Python 3.11+**.

```bash
npm install
npm run data:refresh   # Fetch verified data into public/data/
npm run dev            # Start Vite dev server
npm run build          # Build canonical frontend into dist/
npm run test:all       # Run Vitest (JS) + unittest (Python) suites
```

## Platform Builds

- **Web (GitHub Pages)**: `npm run build` outputs to `dist/` with relative `./` paths. Deployed automatically via `.github/workflows/deploy-pages.yml`.
- **Windows (Electron)**: `npm run build-win` produces an NSIS installer in `release/`. Hardened with `nodeIntegration: false`, `contextIsolation: true`, `sandbox: true`, `contextBridge`, strict CSP, and `https://`-only external links.
- **Android (Capacitor 8)**: `npm run cap:sync` syncs `dist/` into `android/`, built via `./gradlew assembleDebug` in `.github/workflows/build-apk.yml`.

## Optional GitHub Actions Secrets

- `ARTIFICIAL_ANALYSIS_API_KEY` — Enables automated retrieval of Artificial Analysis benchmark indices in `.github/workflows/data-refresh.yml`.

## License

MIT License — see `LICENSE`.
