/**
 * Local Persistence for Personal Workspace (no account required).
 */

const STORAGE_KEY = 'linacre_llm_hub_workspace_v1';

export function getDefaultWorkspace() {
  return {
    favourites: [],
    recentlyViewed: [],
    savedComparisons: [],
    hardwareProfiles: [
      {
        id: 'default-profile',
        name: 'Desktop 16GB VRAM / 32GB RAM',
        gpuModel: 'RTX 4080 / RX 7800 XT',
        gpuVramGb: 16,
        systemRamGb: 32,
        cpu: 'Modern 8-core CPU',
        os: 'Windows 11 / Linux',
        diskSpaceGb: 250
      }
    ],
    ollamaEndpoint: '',
    preferences: {
      reducedMotion: false
    }
  };
}

export function loadWorkspace(storage = globalThis.localStorage) {
  try {
    if (!storage) return getDefaultWorkspace();
    const raw = storage.getItem(STORAGE_KEY);
    if (!raw) return getDefaultWorkspace();
    const parsed = JSON.parse(raw);
    return {
      ...getDefaultWorkspace(),
      ...parsed,
      preferences: {
        ...getDefaultWorkspace().preferences,
        ...(parsed.preferences || {})
      }
    };
  } catch {
    return getDefaultWorkspace();
  }
}

export function saveWorkspace(workspace, storage = globalThis.localStorage) {
  try {
    if (!storage) return false;
    storage.setItem(STORAGE_KEY, JSON.stringify(workspace));
    return true;
  } catch {
    return false;
  }
}

export function toggleFavourite(workspace, item) {
  const exists = workspace.favourites.some((f) => f.id === item.id);
  const favourites = exists
    ? workspace.favourites.filter((f) => f.id !== item.id)
    : [{ ...item, savedAt: new Date().toISOString() }, ...workspace.favourites].slice(0, 50);
  return { ...workspace, favourites };
}

export function recordRecentlyViewed(workspace, item) {
  const filtered = workspace.recentlyViewed.filter((r) => r.id !== item.id);
  const recentlyViewed = [{ ...item, viewedAt: new Date().toISOString() }, ...filtered].slice(0, 20);
  return { ...workspace, recentlyViewed };
}

export function exportWorkspaceJson(workspace) {
  return JSON.stringify(
    {
      exported_at: new Date().toISOString(),
      application: 'Linacre LLM Hub',
      workspace
    },
    null,
    2
  );
}
