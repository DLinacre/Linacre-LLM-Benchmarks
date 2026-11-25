import { loadAllDatasets, filterAndSortItems, connectLocalOllama } from './lib/data.js';
import { estimateHardwareCompatibility, QUANTISATION_BPP, MODEL_FORMATS } from './lib/hardware.js';
import { formatUsd, calculateTokenCost } from './lib/pricing.js';
import {
  loadWorkspace,
  saveWorkspace,
  toggleFavourite,
  recordRecentlyViewed,
  exportWorkspaceJson
} from './lib/storage.js';

const VIEW_META = {
  dashboard: { title: 'AI Intelligence Dashboard', subtitle: 'Verified data from official APIs with full provenance' },
  leaderboards: { title: 'Global AI Leaderboards', subtitle: 'Independent methodologies — never merged across incompatible scales' },
  compare: { title: 'Model Comparison', subtitle: 'Side-by-side comparison of verified model metadata and pricing' },
  hardware: { title: 'Hardware Compatibility Calculator', subtitle: 'Transparent VRAM, KV cache & offloading estimator for local AI' },
  local: { title: 'Local AI Explorer', subtitle: 'Hugging Face GGUF models & user-configured local Ollama connection' },
  pricing: { title: 'AI Pricing Intelligence', subtitle: 'Published provider token pricing & interactive cost calculator' },
  trending: { title: 'Open-Source AI Projects', subtitle: 'Verified GitHub repository metrics (no fabricated growth velocity)' },
  releases: { title: 'AI News & Releases', subtitle: 'Official project releases with publication vs event dates' },
  workspace: { title: 'Personal Workspace', subtitle: 'Local favourites, recently viewed items, hardware profiles & export' },
  sources: { title: 'Data Sources & Transparency', subtitle: 'Provider status, auth requirements, rate limits & known limitations' }
};

function esc(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmtNum(val) {
  if (val === null || val === undefined || !Number.isFinite(Number(val))) return 'No Data Available';
  return Number(val).toLocaleString();
}

function fmtDate(iso) {
  if (!iso) return 'No Data Available';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'No Data Available';
  return d.toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
}

function statusBadge(status) {
  if (status === 'healthy') return '<span class="badge badge-healthy">Healthy</span>';
  if (status === 'not_configured') return '<span class="badge badge-warn">Not Configured</span>';
  if (status === 'user_configured') return '<span class="badge badge-info">User Configured</span>';
  return '<span class="badge badge-error">Unavailable</span>';
}

const state = {
  view: 'dashboard',
  datasets: null,
  workspace: loadWorkspace(),
  compareSelection: [],
  ollamaState: { status: 'Not Connected', models: [], error: null, endpoint: '' },
  hardwareInput: {
    gpuModel: 'RTX 4080',
    gpuVramGb: 16,
    systemRamGb: 32,
    cpu: '8-core Desktop CPU',
    os: 'Windows 11',
    diskSpaceGb: 250,
    parametersBillions: 8,
    contextWindow: 8192,
    modelFormat: 'GGUF',
    quantisation: 'Q4_K_M'
  }
};

function persistWorkspace() {
  saveWorkspace(state.workspace);
}

function setView(viewName) {
  if (!VIEW_META[viewName]) return;
  state.view = viewName;
  document.querySelectorAll('.nav-item').forEach((btn) => {
    const active = btn.dataset.view === viewName;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-selected', String(active));
  });
  document.getElementById('viewTitle').textContent = VIEW_META[viewName].title;
  document.getElementById('viewSubtitle').textContent = VIEW_META[viewName].subtitle;
  document.querySelector('.sidebar')?.classList.remove('open');
  renderCurrentView();
}

function renderDashboard(container) {
  const repos = state.datasets?.trendingRepos?.data || [];
  const releases = state.datasets?.releases?.data || [];
  const catalog = state.datasets?.catalog?.data || [];
  const sources = state.datasets?.sources?.data || [];
  const healthyCount = sources.filter((s) => s.status === 'healthy').length;

  container.innerHTML = `
    <div class="grid-4">
      <div class="card">
        <div class="stat-label">Verified Sources Active</div>
        <div class="stat-value">${healthyCount} / ${sources.length}</div>
        <div class="stat-sub">Official APIs only</div>
      </div>
      <div class="card">
        <div class="stat-label">Open-Source AI Repos</div>
        <div class="stat-value">${repos.length > 0 ? repos.length : 'No Data'}</div>
        <div class="stat-sub">GitHub REST API</div>
      </div>
      <div class="card">
        <div class="stat-label">Tracked Releases</div>
        <div class="stat-value">${releases.length > 0 ? releases.length : 'No Data'}</div>
        <div class="stat-sub">GitHub Releases API</div>
      </div>
      <div class="card">
        <div class="stat-label">Catalogued API Models</div>
        <div class="stat-value">${catalog.length > 0 ? fmtNum(catalog.length) : 'No Data'}</div>
        <div class="stat-sub">OpenRouter Catalogue</div>
      </div>
    </div>

    <div class="grid-2">
      <section class="card">
        <div class="card-header">
          <h3 class="card-title">Top Open-Source AI Repositories</h3>
          <button class="btn btn-secondary btn-sm" data-goto="trending">View All</button>
        </div>
        ${repos.length === 0 ? '<p class="stat-sub">No Data Available</p>' : `
          <div class="table-wrap">
            <table>
              <thead><tr><th>Repository</th><th>Category</th><th>Stars</th></tr></thead>
              <tbody>
                ${repos.slice(0, 6).map((r) => `
                  <tr>
                    <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener noreferrer">${esc(r.repo_name)}</a></td>
                    <td>${esc(r.category)}</td>
                    <td class="mono">${fmtNum(r.stars)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `}
      </section>

      <section class="card">
        <div class="card-header">
          <h3 class="card-title">Latest Official AI Releases</h3>
          <button class="btn btn-secondary btn-sm" data-goto="releases">View All</button>
        </div>
        ${releases.length === 0 ? '<p class="stat-sub">No Data Available</p>' : `
          <div class="table-wrap">
            <table>
              <thead><tr><th>Project</th><th>Release</th><th>Published</th></tr></thead>
              <tbody>
                ${releases.slice(0, 6).map((rel) => `
                  <tr>
                    <td>${esc(rel.project)}</td>
                    <td><a href="${esc(rel.source_url)}" target="_blank" rel="noopener noreferrer">${esc(rel.tag || rel.title)}</a></td>
                    <td class="mono">${fmtDate(rel.published_at)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `}
      </section>
    </div>

    <section class="card">
      <div class="card-header">
        <h3 class="card-title">Source Health &amp; Your Workspace</h3>
        <button class="btn btn-secondary btn-sm" data-goto="sources">Transparency Report</button>
      </div>
      <p class="stat-sub">
        Saved favourites: <strong>${state.workspace.favourites.length}</strong> &middot;
        Recently viewed: <strong>${state.workspace.recentlyViewed.length}</strong> &middot;
        Hardware profiles: <strong>${state.workspace.hardwareProfiles.length}</strong>
      </p>
    </section>
  `;

  container.querySelectorAll('[data-goto]').forEach((btn) => {
    btn.addEventListener('click', () => setView(btn.dataset.goto));
  });
}

function renderLeaderboards(container) {
  const lb = state.datasets?.leaderboards?.data;
  const categories = lb?.categories || {};
  const keys = Object.keys(categories);

  container.innerHTML = `
    <div class="notice-box">
      <strong>Methodology Policy:</strong> ${esc(lb?.methodology_notice || 'Independent leaderboards are never combined into a fabricated overall score.')}
    </div>
    <div class="toolbar">
      <select id="lbCategorySelect" aria-label="Select benchmark category">
        ${keys.map((k) => `<option value="${esc(k)}">${esc(categories[k].title)}</option>`).join('')}
      </select>
      <input type="text" id="lbSearch" placeholder="Filter models or creators…" aria-label="Filter leaderboard" />
    </div>
    <div id="lbContent"></div>
  `;

  const select = container.querySelector('#lbCategorySelect');
  const search = container.querySelector('#lbSearch');
  const content = container.querySelector('#lbContent');

  function draw() {
    const cat = categories[select.value];
    if (!cat) {
      content.innerHTML = '<div class="empty-state"><h3>No Data Available</h3></div>';
      return;
    }
    const entries = filterAndSortItems(cat.entries || [], { query: search.value, sortBy: 'score' });
    if (entries.length === 0) {
      content.innerHTML = `
        <div class="empty-state">
          <h3>Not Configured / No Data Available</h3>
          <p>${esc(cat.methodology)}</p>
          <p style="margin-top:8px;">Configure <code>ARTIFICIAL_ANALYSIS_API_KEY</code> in GitHub Actions secrets to populate verified ${esc(cat.title)} results from <a href="${esc(cat.source_url)}" target="_blank" rel="noopener noreferrer">${esc(cat.source_name)}</a>. Linacre LLM Hub never fabricates benchmark scores.</p>
        </div>
      `;
      return;
    }
    content.innerHTML = `
      <p class="stat-sub" style="margin-bottom:10px;">
        <strong>Methodology:</strong> ${esc(cat.methodology)} &middot;
        <strong>Source:</strong> <a href="${esc(cat.source_url)}" target="_blank" rel="noopener noreferrer">${esc(cat.source_name)}</a>
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>#</th><th>Model</th><th>Creator</th><th>Score (${esc(cat.unit)})</th><th>Retrieved</th></tr></thead>
          <tbody>
            ${entries.map((e, i) => `
              <tr>
                <td class="mono">${i + 1}</td>
                <td>${esc(e.model_name)}</td>
                <td>${esc(e.creator)}</td>
                <td class="mono">${esc(e.score)}</td>
                <td class="mono">${fmtDate(e.retrieved_at)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  select.addEventListener('change', draw);
  search.addEventListener('input', draw);
  draw();
}

function renderCompare(container) {
  const catalog = state.datasets?.catalog?.data || [];
  if (catalog.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <h3>No Data Available</h3>
        <p>Model catalogue data from OpenRouter is currently unavailable in this build. Once refreshed via GitHub Actions, you can select and compare models side by side here.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="toolbar">
      <select id="compareAddSelect" aria-label="Choose model to compare">
        <option value="">Select a model to add…</option>
        ${catalog.slice(0, 150).map((m) => `<option value="${esc(m.model_id)}">${esc(m.model_name)} (${esc(m.creator)})</option>`).join('')}
      </select>
      <button id="compareAddBtn" class="btn">Add to Comparison</button>
      <button id="compareClearBtn" class="btn btn-secondary">Clear</button>
    </div>
    <div id="compareTable"></div>
  `;

  const select = container.querySelector('#compareAddSelect');
  const tableDiv = container.querySelector('#compareTable');

  function draw() {
    const selected = state.compareSelection
      .map((id) => catalog.find((m) => m.model_id === id))
      .filter(Boolean);

    if (selected.length === 0) {
      tableDiv.innerHTML = '<div class="empty-state"><h3>Select up to 4 models to compare</h3><p>Compare context windows, input/output/cached pricing, modalities, and provider links.</p></div>';
      return;
    }

    tableDiv.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Attribute</th>
              ${selected.map((m) => `<th>${esc(m.model_name)}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            <tr><td>Creator</td>${selected.map((m) => `<td>${esc(m.creator)}</td>`).join('')}</tr>
            <tr><td>Context Window</td>${selected.map((m) => `<td class="mono">${fmtNum(m.context_length)}</td>`).join('')}</tr>
            <tr><td>Input / 1M Tokens</td>${selected.map((m) => `<td class="mono">${formatUsd(m.input_price_per_1m)}</td>`).join('')}</tr>
            <tr><td>Output / 1M Tokens</td>${selected.map((m) => `<td class="mono">${formatUsd(m.output_price_per_1m)}</td>`).join('')}</tr>
            <tr><td>Cached Input / 1M</td>${selected.map((m) => `<td class="mono">${formatUsd(m.cached_input_price_per_1m)}</td>`).join('')}</tr>
            <tr><td>Modalities</td>${selected.map((m) => `<td>${esc((m.modalities || []).join(', ') || 'No Data Available')}</td>`).join('')}</tr>
            <tr><td>License</td>${selected.map((m) => `<td>${esc(m.license || 'No Data Available')}</td>`).join('')}</tr>
            <tr><td>Source</td>${selected.map((m) => `<td><a href="${esc(m.source_url)}" target="_blank" rel="noopener noreferrer">Provider Page</a></td>`).join('')}</tr>
          </tbody>
        </table>
      </div>
    `;
  }

  container.querySelector('#compareAddBtn').addEventListener('click', () => {
    const id = select.value;
    if (id && !state.compareSelection.includes(id) && state.compareSelection.length < 4) {
      state.compareSelection.push(id);
      const model = catalog.find((m) => m.model_id === id);
      if (model) {
        state.workspace = recordRecentlyViewed(state.workspace, { id: model.model_id, name: model.model_name, type: 'model' });
        persistWorkspace();
      }
      draw();
    }
  });

  container.querySelector('#compareClearBtn').addEventListener('click', () => {
    state.compareSelection = [];
    draw();
  });

  draw();
}

function renderHardware(container) {
  const hw = state.hardwareInput;
  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <h3 class="card-title" style="margin-bottom:14px;">System &amp; Model Configuration</h3>
      <form id="hwForm" class="form-grid">
        <div class="field"><label for="hwGpu">GPU Model</label><input id="hwGpu" type="text" value="${esc(hw.gpuModel)}" /></div>
        <div class="field"><label for="hwVram">GPU VRAM (GB)</label><input id="hwVram" type="number" min="0" step="1" value="${esc(hw.gpuVramGb)}" /></div>
        <div class="field"><label for="hwRam">System RAM (GB)</label><input id="hwRam" type="number" min="1" step="1" value="${esc(hw.systemRamGb)}" /></div>
        <div class="field"><label for="hwCpu">CPU</label><input id="hwCpu" type="text" value="${esc(hw.cpu)}" /></div>
        <div class="field"><label for="hwOs">Operating System</label><input id="hwOs" type="text" value="${esc(hw.os)}" /></div>
        <div class="field"><label for="hwDisk">Available Disk (GB)</label><input id="hwDisk" type="number" min="1" step="1" value="${esc(hw.diskSpaceGb)}" /></div>
        <div class="field"><label for="hwParams">Model Parameters (Billions)</label><input id="hwParams" type="number" min="0.5" step="0.5" value="${esc(hw.parametersBillions)}" /></div>
        <div class="field"><label for="hwCtx">Context Window (Tokens)</label><input id="hwCtx" type="number" min="512" step="512" value="${esc(hw.contextWindow)}" /></div>
        <div class="field">
          <label for="hwFormat">Model Format</label>
          <select id="hwFormat">${MODEL_FORMATS.map((f) => `<option value="${f}" ${hw.modelFormat === f ? 'selected' : ''}>${f}</option>`).join('')}</select>
        </div>
        <div class="field">
          <label for="hwQuant">Quantisation</label>
          <select id="hwQuant">${Object.entries(QUANTISATION_BPP).map(([k, v]) => `<option value="${k}" ${hw.quantisation === k ? 'selected' : ''}>${esc(v.label)}</option>`).join('')}</select>
        </div>
      </form>
      <div class="toolbar" style="margin-bottom:0;">
        <button id="hwCalcBtn" class="btn">Calculate Compatibility</button>
        <button id="hwSaveProfileBtn" class="btn btn-secondary">Save Hardware Profile</button>
      </div>
    </div>
    <div id="hwResult"></div>
  `;

  const resultEl = container.querySelector('#hwResult');

  function runCalc() {
    state.hardwareInput = {
      gpuModel: container.querySelector('#hwGpu').value,
      gpuVramGb: Number(container.querySelector('#hwVram').value),
      systemRamGb: Number(container.querySelector('#hwRam').value),
      cpu: container.querySelector('#hwCpu').value,
      os: container.querySelector('#hwOs').value,
      diskSpaceGb: Number(container.querySelector('#hwDisk').value),
      parametersBillions: Number(container.querySelector('#hwParams').value),
      contextWindow: Number(container.querySelector('#hwCtx').value),
      modelFormat: container.querySelector('#hwFormat').value,
      quantisation: container.querySelector('#hwQuant').value
    };

    const res = estimateHardwareCompatibility(state.hardwareInput);
    if (!res.valid) {
      resultEl.innerHTML = `<div class="empty-state"><h3>${esc(res.classification)}</h3><p>${esc(res.error)}</p></div>`;
      return;
    }

    const badgeClass =
      res.classification === 'Excellent fit' ? 'badge-healthy' :
      res.classification === 'Good fit' ? 'badge-info' :
      res.classification === 'Limited fit' ? 'badge-warn' : 'badge-error';

    resultEl.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Estimated Compatibility</h3>
          <span class="badge ${badgeClass}">${esc(res.classification)}</span>
        </div>
        <p style="margin-bottom:14px;">${esc(res.summary)}</p>
        <div class="grid-4">
          <div><div class="stat-label">Model Weights</div><div class="stat-value">${res.estimates.weightMemoryGb} GB</div></div>
          <div><div class="stat-label">KV Cache Est.</div><div class="stat-value">${res.estimates.kvCacheGb} GB</div></div>
          <div><div class="stat-label">Runtime Overhead</div><div class="stat-value">${res.estimates.runtimeOverheadGb} GB</div></div>
          <div><div class="stat-label">Total Memory</div><div class="stat-value">${res.estimates.totalRequiredGb} GB</div></div>
        </div>
        <p class="stat-sub">
          Estimated GPU Offload: <strong>${res.estimates.gpuOffloadPercent}%</strong> &middot;
          CPU/RAM Spillover: <strong>${res.estimates.cpuSpilloverGb} GB</strong> &middot;
          VRAM Headroom: <strong>${res.estimates.vramHeadroomGb} GB</strong> &middot;
          Disk Needed: <strong>${res.estimates.requiredDiskGb} GB</strong>
        </p>
        <div class="notice-box" style="margin-top:14px;margin-bottom:0;">
          <strong>Disclosed Assumptions (Estimates Only):</strong>
          <ul style="margin-left:18px;margin-top:6px;">
            ${res.assumptions.map((a) => `<li>${esc(a)}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  }

  container.querySelector('#hwCalcBtn').addEventListener('click', runCalc);
  container.querySelector('#hwSaveProfileBtn').addEventListener('click', () => {
    runCalc();
    const profile = {
      id: `profile-${Date.now()}`,
      name: `${state.hardwareInput.gpuModel || 'Custom'} (${state.hardwareInput.gpuVramGb}GB VRAM / ${state.hardwareInput.systemRamGb}GB RAM)`,
      ...state.hardwareInput
    };
    state.workspace.hardwareProfiles = [profile, ...state.workspace.hardwareProfiles].slice(0, 10);
    persistWorkspace();
    alert('Hardware profile saved to your Personal Workspace.');
  });

  runCalc();
}

function renderLocalExplorer(container) {
  const localModels = state.datasets?.localModels?.data || [];
  const savedEndpoint = state.workspace.ollamaEndpoint || 'http://127.0.0.1:11434';

  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div class="card-header">
        <h3 class="card-title">Local Ollama Connection (Explicit Opt-In)</h3>
        <span id="ollamaBadge" class="badge badge-info">${esc(state.ollamaState.status)}</span>
      </div>
      <p class="stat-sub" style="margin-bottom:12px;">Linacre LLM Hub never scans your network automatically. Enter your local Ollama URL and click Connect to list installed models.</p>
      <div class="toolbar" style="margin-bottom:8px;">
        <input id="ollamaUrlInput" type="url" value="${esc(savedEndpoint)}" placeholder="http://127.0.0.1:11434" style="min-width:260px;" aria-label="Ollama local endpoint URL" />
        <button id="ollamaConnectBtn" class="btn">Connect to Ollama</button>
      </div>
      <div id="ollamaResult"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Hugging Face GGUF &amp; Open-Weight Models</h3>
      </div>
      <div class="toolbar">
        <input id="localSearch" type="text" placeholder="Search GGUF models, creators, licenses…" aria-label="Search local models" />
      </div>
      <div id="localList"></div>
    </div>
  `;

  const ollamaResult = container.querySelector('#ollamaResult');
  const ollamaBadge = container.querySelector('#ollamaBadge');

  function drawOllama() {
    if (state.ollamaState.error) {
      ollamaResult.innerHTML = `<p class="stat-sub" style="color:var(--accent-amber);">${esc(state.ollamaState.error)}</p>`;
    } else if (state.ollamaState.models.length > 0) {
      ollamaResult.innerHTML = `
        <div class="table-wrap" style="margin-top:10px;">
          <table>
            <thead><tr><th>Installed Model</th><th>Size</th><th>Modified</th></tr></thead>
            <tbody>
              ${state.ollamaState.models.map((m) => `
                <tr>
                  <td class="mono">${esc(m.name)}</td>
                  <td class="mono">${m.size ? (m.size / (1024 ** 3)).toFixed(2) + ' GB' : 'No Data Available'}</td>
                  <td class="mono">${fmtDate(m.modified_at)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
  }

  container.querySelector('#ollamaConnectBtn').addEventListener('click', async () => {
    const url = container.querySelector('#ollamaUrlInput').value;
    state.workspace.ollamaEndpoint = url;
    persistWorkspace();
    ollamaBadge.textContent = 'Connecting…';
    const res = await connectLocalOllama(url);
    if (res.ok) {
      state.ollamaState = { status: 'Connected', models: res.models, error: null, endpoint: res.endpoint };
      ollamaBadge.textContent = `Connected (${res.models.length} models)`;
    } else {
      state.ollamaState = { status: 'Connection Failed', models: [], error: res.error, endpoint: url };
      ollamaBadge.textContent = 'Connection Failed';
    }
    drawOllama();
  });

  const localSearch = container.querySelector('#localSearch');
  const localList = container.querySelector('#localList');

  function drawLocal() {
    const filtered = filterAndSortItems(localModels, { query: localSearch.value, sortBy: 'downloads' });
    if (filtered.length === 0) {
      localList.innerHTML = '<div class="empty-state"><h3>No Data Available</h3><p>Hugging Face GGUF catalogue will populate automatically when the scheduled data refresh runs with outbound Hugging Face Hub access.</p></div>';
      return;
    }
    localList.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Model</th><th>Creator</th><th>Format</th><th>License</th><th>Downloads</th><th>Link</th></tr></thead>
          <tbody>
            ${filtered.map((m) => `
              <tr>
                <td>${esc(m.model_name)}</td>
                <td>${esc(m.creator)}</td>
                <td class="mono">${esc(m.format)}</td>
                <td>${esc(m.license)}</td>
                <td class="mono">${fmtNum(m.downloads)}</td>
                <td><a href="${esc(m.source_url)}" target="_blank" rel="noopener noreferrer">Hugging Face</a></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  localSearch.addEventListener('input', drawLocal);
  drawOllama();
  drawLocal();
}

function renderPricing(container) {
  const catalog = state.datasets?.catalog?.data || [];

  container.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <h3 class="card-title" style="margin-bottom:12px;">Interactive Token-Cost Calculator</h3>
      <div class="form-grid">
        <div class="field"><label for="pcInPrice">Input Price ($ / 1M tokens)</label><input id="pcInPrice" type="number" min="0" step="0.01" value="0.50" /></div>
        <div class="field"><label for="pcOutPrice">Output Price ($ / 1M tokens)</label><input id="pcOutPrice" type="number" min="0" step="0.01" value="1.50" /></div>
        <div class="field"><label for="pcInTok">Input Tokens / Request</label><input id="pcInTok" type="number" min="0" step="100" value="2000" /></div>
        <div class="field"><label for="pcOutTok">Output Tokens / Request</label><input id="pcOutTok" type="number" min="0" step="100" value="800" /></div>
        <div class="field"><label for="pcReqs">Requests</label><input id="pcReqs" type="number" min="1" step="10" value="1000" /></div>
      </div>
      <div id="pcOutput" class="stat-sub"></div>
    </div>

    <div class="card">
      <div class="card-header"><h3 class="card-title">Published Provider Pricing</h3></div>
      ${catalog.length === 0 ? '<div class="empty-state"><h3>No Data Available</h3><p>OpenRouter published pricing catalogue is not yet populated in this offline snapshot.</p></div>' : `
        <div class="toolbar">
          <input id="priceSearch" type="text" placeholder="Filter models or creators…" aria-label="Filter pricing table" />
        </div>
        <div id="priceTable"></div>
      `}
    </div>
  `;

  function updateCalc() {
    const res = calculateTokenCost({
      inputPricePer1M: container.querySelector('#pcInPrice').value,
      outputPricePer1M: container.querySelector('#pcOutPrice').value,
      inputTokens: container.querySelector('#pcInTok').value,
      outputTokens: container.querySelector('#pcOutTok').value,
      requests: container.querySelector('#pcReqs').value
    });
    const out = container.querySelector('#pcOutput');
    if (!res.valid) {
      out.textContent = res.error;
      return;
    }
    out.innerHTML = `Estimated Input: <strong class="mono">${formatUsd(res.inputCost)}</strong> &middot; Output: <strong class="mono">${formatUsd(res.outputCost)}</strong> &middot; <strong>Total: <span class="mono" style="color:var(--accent-cyan);">${formatUsd(res.totalCost)}</span></strong>`;
  }

  ['#pcInPrice', '#pcOutPrice', '#pcInTok', '#pcOutTok', '#pcReqs'].forEach((sel) => {
    container.querySelector(sel).addEventListener('input', updateCalc);
  });
  updateCalc();

  if (catalog.length > 0) {
    const search = container.querySelector('#priceSearch');
    const tableDiv = container.querySelector('#priceTable');
    function drawTable() {
      const items = filterAndSortItems(catalog, { query: search.value, sortBy: 'price_asc' }).slice(0, 60);
      tableDiv.innerHTML = `
        <div class="table-wrap">
          <table>
            <thead><tr><th>Model</th><th>Context</th><th>Input / 1M</th><th>Output / 1M</th><th>Cached / 1M</th><th>Free Tier</th></tr></thead>
            <tbody>
              ${items.map((m) => `
                <tr>
                  <td><a href="${esc(m.source_url)}" target="_blank" rel="noopener noreferrer">${esc(m.model_name)}</a></td>
                  <td class="mono">${fmtNum(m.context_length)}</td>
                  <td class="mono">${formatUsd(m.input_price_per_1m)}</td>
                  <td class="mono">${formatUsd(m.output_price_per_1m)}</td>
                  <td class="mono">${formatUsd(m.cached_input_price_per_1m)}</td>
                  <td>${m.free_tier_available ? '<span class="badge badge-healthy">Verified Free</span>' : 'Paid / Standard'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
    search.addEventListener('input', drawTable);
    drawTable();
  }
}

function renderTrending(container) {
  const repos = state.datasets?.trendingRepos?.data || [];
  const categories = ['all', ...new Set(repos.map((r) => r.category).filter(Boolean))];
  const languages = ['all', ...new Set(repos.map((r) => r.language).filter(Boolean))];

  container.innerHTML = `
    <div class="toolbar">
      <input id="repoSearch" type="text" placeholder="Search repositories…" aria-label="Search repositories" />
      <select id="repoCat" aria-label="Filter by category">${categories.map((c) => `<option value="${esc(c)}">${esc(c === 'all' ? 'All Categories' : c)}</option>`).join('')}</select>
      <select id="repoLang" aria-label="Filter by language">${languages.map((l) => `<option value="${esc(l)}">${esc(l === 'all' ? 'All Languages' : l)}</option>`).join('')}</select>
      <select id="repoSort" aria-label="Sort repositories">
        <option value="stars">Sort: Stars</option>
        <option value="updated">Sort: Recently Updated</option>
      </select>
    </div>
    <div id="repoTable"></div>
  `;

  const search = container.querySelector('#repoSearch');
  const cat = container.querySelector('#repoCat');
  const lang = container.querySelector('#repoLang');
  const sort = container.querySelector('#repoSort');
  const tableDiv = container.querySelector('#repoTable');

  function draw() {
    const items = filterAndSortItems(repos, {
      query: search.value,
      category: cat.value,
      language: lang.value,
      sortBy: sort.value
    });

    if (items.length === 0) {
      tableDiv.innerHTML = '<div class="empty-state"><h3>No Data Available</h3><p>No repositories match your filters.</p></div>';
      return;
    }

    tableDiv.innerHTML = `
      <div class="table-wrap">
        <table>
          <thead><tr><th>Repository</th><th>Category</th><th>Language</th><th>Stars</th><th>Forks</th><th>License</th><th>Updated</th><th>Save</th></tr></thead>
          <tbody>
            ${items.map((r) => {
              const isFav = state.workspace.favourites.some((f) => f.id === r.source_id);
              return `
                <tr>
                  <td>
                    <a href="${esc(r.source_url)}" target="_blank" rel="noopener noreferrer"><strong>${esc(r.repo_name)}</strong></a>
                    <div class="stat-sub">${esc(r.description)}</div>
                  </td>
                  <td>${esc(r.category)}</td>
                  <td class="mono">${esc(r.language)}</td>
                  <td class="mono">${fmtNum(r.stars)}</td>
                  <td class="mono">${fmtNum(r.forks)}</td>
                  <td class="mono">${esc(r.license)}</td>
                  <td class="mono">${fmtDate(r.updated_at)}</td>
                  <td><button class="btn btn-secondary btn-sm fav-btn" data-id="${esc(r.source_id)}" data-name="${esc(r.repo_name)}">${isFav ? 'Saved' : 'Save'}</button></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;

    tableDiv.querySelectorAll('.fav-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.workspace = toggleFavourite(state.workspace, { id: btn.dataset.id, name: btn.dataset.name, type: 'repo' });
        persistWorkspace();
        draw();
      });
    });
  }

  [search, cat, lang, sort].forEach((el) => el.addEventListener('input', draw));
  draw();
}

function renderReleases(container) {
  const releases = state.datasets?.releases?.data || [];
  if (releases.length === 0) {
    container.innerHTML = '<div class="empty-state"><h3>No Data Available</h3><p>No verified releases have been retrieved yet.</p></div>';
    return;
  }

  container.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Project</th><th>Release</th><th>Category</th><th>Published Date</th><th>Event Date</th><th>Source</th></tr></thead>
        <tbody>
          ${releases.map((r) => `
            <tr>
              <td><strong>${esc(r.project)}</strong></td>
              <td>${esc(r.title)} <span class="badge badge-info">${esc(r.tag || '')}</span></td>
              <td>${esc(r.category)}</td>
              <td class="mono">${fmtDate(r.published_at)}</td>
              <td class="mono">${fmtDate(r.event_date)}</td>
              <td><a href="${esc(r.source_url)}" target="_blank" rel="noopener noreferrer">Official Release</a></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderWorkspace(container) {
  const ws = state.workspace;
  container.innerHTML = `
    <div class="toolbar">
      <button id="exportWsBtn" class="btn">Export Workspace JSON</button>
    </div>
    <div class="grid-2">
      <section class="card">
        <h3 class="card-title" style="margin-bottom:10px;">Saved Favourites (${ws.favourites.length})</h3>
        ${ws.favourites.length === 0 ? '<p class="stat-sub">No saved favourites yet. Save repositories or models from any section.</p>' : `
          <ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">
            ${ws.favourites.map((f) => `<li class="mono">${esc(f.name)} <span class="badge badge-info">${esc(f.type)}</span></li>`).join('')}
          </ul>
        `}
      </section>
      <section class="card">
        <h3 class="card-title" style="margin-bottom:10px;">Saved Hardware Profiles (${ws.hardwareProfiles.length})</h3>
        <ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">
          ${ws.hardwareProfiles.map((p) => `<li><strong>${esc(p.name)}</strong> — ${esc(p.gpuVramGb)}GB VRAM / ${esc(p.systemRamGb)}GB RAM</li>`).join('')}
        </ul>
      </section>
    </div>
  `;

  container.querySelector('#exportWsBtn').addEventListener('click', () => {
    const blob = new Blob([exportWorkspaceJson(state.workspace)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'linacre-llm-hub-workspace.json';
    a.click();
    URL.revokeObjectURL(url);
  });
}

function renderSources(container) {
  const sources = state.datasets?.sources?.data || [];
  container.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Status</th>
            <th>Access Tier</th>
            <th>Auth Required</th>
            <th>Last Retrieval</th>
            <th>Records</th>
            <th>Known Limitations</th>
          </tr>
        </thead>
        <tbody>
          ${sources.map((s) => `
            <tr>
              <td><a href="${esc(s.official_url)}" target="_blank" rel="noopener noreferrer"><strong>${esc(s.name)}</strong></a><div class="stat-sub">${esc(s.data_obtained)}</div></td>
              <td>${statusBadge(s.status)}</td>
              <td>${esc(s.access_tier)}</td>
              <td>${esc(s.auth_required)}</td>
              <td class="mono">${fmtDate(s.last_successful_retrieval)}</td>
              <td class="mono">${fmtNum(s.record_count)}</td>
              <td class="stat-sub">${esc(s.limitations)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderCurrentView() {
  const container = document.getElementById('viewContainer');
  if (!container) return;
  const renderers = {
    dashboard: renderDashboard,
    leaderboards: renderLeaderboards,
    compare: renderCompare,
    hardware: renderHardware,
    local: renderLocalExplorer,
    pricing: renderPricing,
    trending: renderTrending,
    releases: renderReleases,
    workspace: renderWorkspace,
    sources: renderSources
  };
  (renderers[state.view] || renderDashboard)(container);
}

async function init() {
  document.querySelectorAll('.nav-item').forEach((btn) => {
    btn.addEventListener('click', () => setView(btn.dataset.view));
  });

  document.getElementById('mobileMenuBtn')?.addEventListener('click', () => {
    document.querySelector('.sidebar')?.classList.toggle('open');
  });

  state.datasets = await loadAllDatasets();
  const updatedAt = state.datasets?.sources?.retrieved_at;
  const badge = document.getElementById('lastUpdatedBadge');
  if (badge) {
    badge.textContent = updatedAt ? `Verified: ${fmtDate(updatedAt)}` : 'Offline / No Data';
  }
  renderCurrentView();
}

document.addEventListener('DOMContentLoaded', init);
