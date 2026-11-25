import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { estimateHardwareCompatibility } from '../../src/lib/hardware.js';
import { calculateTokenCost, formatUsd } from '../../src/lib/pricing.js';
import { filterAndSortItems, validateOllamaEndpoint } from '../../src/lib/data.js';
import {
  getDefaultWorkspace,
  toggleFavourite,
  recordRecentlyViewed,
  exportWorkspaceJson
} from '../../src/lib/storage.js';

describe('Hardware Compatibility Calculator', () => {
  it('classifies an 8B Q4_K_M model on 16GB VRAM as Excellent fit', () => {
    const res = estimateHardwareCompatibility({
      gpuVramGb: 16,
      systemRamGb: 32,
      diskSpaceGb: 100,
      parametersBillions: 8,
      contextWindow: 8192,
      modelFormat: 'GGUF',
      quantisation: 'Q4_K_M'
    });
    expect(res.valid).toBe(true);
    expect(res.classification).toBe('Excellent fit');
    expect(res.estimates.gpuOffloadPercent).toBe(100);
    expect(res.assumptions.length).toBeGreaterThan(0);
  });

  it('classifies a 70B Q4_K_M model on 24GB VRAM / 64GB RAM as Limited fit with hybrid offload', () => {
    const res = estimateHardwareCompatibility({
      gpuVramGb: 24,
      systemRamGb: 64,
      diskSpaceGb: 200,
      parametersBillions: 70,
      contextWindow: 4096,
      modelFormat: 'GGUF',
      quantisation: 'Q4_K_M'
    });
    expect(res.valid).toBe(true);
    expect(res.classification).toBe('Limited fit');
    expect(res.estimates.cpuSpilloverGb).toBeGreaterThan(0);
  });

  it('returns Unlikely to fit when disk space is insufficient', () => {
    const res = estimateHardwareCompatibility({
      gpuVramGb: 24,
      systemRamGb: 64,
      diskSpaceGb: 2,
      parametersBillions: 8,
      contextWindow: 4096,
      modelFormat: 'GGUF',
      quantisation: 'Q4_K_M'
    });
    expect(res.valid).toBe(true);
    expect(res.classification).toBe('Unlikely to fit');
    expect(res.estimates.diskSufficient).toBe(false);
  });

  it('returns No Data Available when parameter count is missing or invalid', () => {
    const res = estimateHardwareCompatibility({ gpuVramGb: 16, systemRamGb: 32, parametersBillions: 0 });
    expect(res.valid).toBe(false);
    expect(res.classification).toBe('No Data Available');
  });
});

describe('Pricing Intelligence Calculator', () => {
  it('formats null/undefined prices as No Data Available', () => {
    expect(formatUsd(null)).toBe('No Data Available');
    expect(formatUsd(undefined)).toBe('No Data Available');
    expect(formatUsd(0)).toBe('$0.00');
    expect(formatUsd(2.5)).toBe('$2.50');
  });

  it('calculates exact token costs including cached input tokens', () => {
    const res = calculateTokenCost({
      inputPricePer1M: 1.0,
      outputPricePer1M: 3.0,
      cachedInputPricePer1M: 0.25,
      inputTokens: 1000,
      outputTokens: 500,
      cachedInputTokens: 2000,
      requests: 1000
    });
    expect(res.valid).toBe(true);
    expect(res.inputCost).toBeCloseTo(1.0, 5);
    expect(res.outputCost).toBeCloseTo(1.5, 5);
    expect(res.cachedCost).toBeCloseTo(0.5, 5);
    expect(res.totalCost).toBeCloseTo(3.0, 5);
  });
});

describe('Search, Filtering & Ollama Validation', () => {
  it('filters by query, category, language and sorts by stars', () => {
    const sample = [
      { repo_name: 'ollama/ollama', category: 'Local AI Runtime', language: 'Go', stars: 100000 },
      { repo_name: 'ggml-org/llama.cpp', category: 'Local AI Runtime', language: 'C++', stars: 75000 },
      { repo_name: 'langchain-ai/langchain', category: 'Agent Framework', language: 'Python', stars: 95000 }
    ];
    const res = filterAndSortItems(sample, { category: 'Local AI Runtime', sortBy: 'stars' });
    expect(res.map((r) => r.repo_name)).toEqual(['ollama/ollama', 'ggml-org/llama.cpp']);
  });

  it('validates Ollama endpoint URLs strictly', () => {
    expect(validateOllamaEndpoint('http://127.0.0.1:11434').valid).toBe(true);
    expect(validateOllamaEndpoint('ftp://localhost:11434').valid).toBe(false);
    expect(validateOllamaEndpoint('not-a-url').valid).toBe(false);
  });
});

describe('Local Workspace Persistence', () => {
  it('toggles favourites, tracks recently viewed, and exports valid JSON', () => {
    let ws = getDefaultWorkspace();
    ws = toggleFavourite(ws, { id: 'github:ollama/ollama', name: 'ollama/ollama', type: 'repo' });
    expect(ws.favourites.length).toBe(1);
    ws = toggleFavourite(ws, { id: 'github:ollama/ollama', name: 'ollama/ollama', type: 'repo' });
    expect(ws.favourites.length).toBe(0);
    ws = recordRecentlyViewed(ws, { id: 'm1', name: 'Model 1', type: 'model' });
    expect(ws.recentlyViewed[0].id).toBe('m1');
    const exported = JSON.parse(exportWorkspaceJson(ws));
    expect(exported.application).toBe('Linacre LLM Hub');
  });
});

describe('Security & Build Configuration', () => {
  it('enforces hardened Electron security settings', async () => {
    const electronMainPath = path.resolve(process.cwd(), 'electron/main.js');
    const content = fs.readFileSync(electronMainPath, 'utf-8');
    expect(content).toContain('nodeIntegration: false');
    expect(content).toContain('contextIsolation: true');
    expect(content).toContain('sandbox: true');
    expect(content).toContain("ALLOWED_EXTERNAL_PROTOCOLS = new Set(['https:'])");
  });

  it('aligns Capacitor webDir to dist/', () => {
    const capConfig = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), 'capacitor.config.json'), 'utf-8'));
    expect(capConfig.webDir).toBe('dist');
    expect(capConfig.appId).toBe('com.linacre.llmhub');
  });

  it('produces dist/index.html with relative asset paths for GitHub Pages / Electron / Capacitor', () => {
    const distHtml = fs.readFileSync(path.resolve(process.cwd(), 'dist/index.html'), 'utf-8');
    expect(distHtml).toContain('./assets/');
  });
});
