/**
 * Data loading, validation, filtering, and explicit user-configured Ollama connection.
 */

export async function fetchDataset(relativePath) {
  try {
    const res = await fetch(relativePath, { cache: 'no-cache' });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const json = await res.json();
    return { ok: true, payload: json };
  } catch (err) {
    return { ok: false, error: err.message, payload: null };
  }
}

export async function loadAllDatasets() {
  const [catalog, leaderboards, localModels, trendingRepos, releases, sources] = await Promise.all([
    fetchDataset('./data/catalog.json'),
    fetchDataset('./data/leaderboards.json'),
    fetchDataset('./data/local_models.json'),
    fetchDataset('./data/trending_repos.json'),
    fetchDataset('./data/releases.json'),
    fetchDataset('./data/sources.json')
  ]);

  return {
    catalog: catalog.payload,
    leaderboards: leaderboards.payload,
    localModels: localModels.payload,
    trendingRepos: trendingRepos.payload,
    releases: releases.payload,
    sources: sources.payload
  };
}

export function filterAndSortItems(items, { query = '', category = 'all', language = 'all', sortBy = 'default' } = {}) {
  const q = query.trim().toLowerCase();
  let result = Array.isArray(items) ? [...items] : [];

  if (q) {
    result = result.filter((item) => {
      const haystack = [
        item.model_name,
        item.model_id,
        item.creator,
        item.repo_name,
        item.description,
        item.title,
        item.project,
        item.category,
        item.language
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(q);
    });
  }

  if (category && category !== 'all') {
    result = result.filter((item) => (item.category || '').toLowerCase() === category.toLowerCase());
  }

  if (language && language !== 'all') {
    result = result.filter((item) => (item.language || '').toLowerCase() === language.toLowerCase());
  }

  if (sortBy === 'stars') {
    result.sort((a, b) => (b.stars || 0) - (a.stars || 0));
  } else if (sortBy === 'price_asc') {
    result.sort((a, b) => (a.input_price_per_1m ?? Infinity) - (b.input_price_per_1m ?? Infinity));
  } else if (sortBy === 'context_desc') {
    result.sort((a, b) => (b.context_length || 0) - (a.context_length || 0));
  } else if (sortBy === 'downloads') {
    result.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
  } else if (sortBy === 'score') {
    result.sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity));
  } else if (sortBy === 'updated') {
    result.sort((a, b) => String(b.updated_at || b.published_at || '').localeCompare(String(a.updated_at || a.published_at || '')));
  }

  return result;
}

export function validateOllamaEndpoint(rawUrl) {
  try {
    const parsed = new URL(rawUrl.trim());
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return { valid: false, error: 'Endpoint must use http:// or https://.' };
    }
    return { valid: true, url: parsed.origin };
  } catch {
    return { valid: false, error: 'Enter a valid URL such as http://127.0.0.1:11434' };
  }
}

export async function connectLocalOllama(endpointUrl) {
  const check = validateOllamaEndpoint(endpointUrl);
  if (!check.valid) {
    return { ok: false, error: check.error, models: [] };
  }
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(`${check.url}/api/tags`, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) {
      return { ok: false, error: `Ollama returned HTTP ${res.status}`, models: [] };
    }
    const json = await res.json();
    return {
      ok: true,
      endpoint: check.url,
      retrievedAt: new Date().toISOString(),
      models: Array.isArray(json.models) ? json.models : []
    };
  } catch (err) {
    return {
      ok: false,
      error: `Could not reach ${check.url}/api/tags (${err.message}). Ensure Ollama is running and CORS is allowed if accessed from a browser.`,
      models: []
    };
  }
}
