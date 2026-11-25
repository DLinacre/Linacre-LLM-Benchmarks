const { app, BrowserWindow, ipcMain, shell, session } = require('electron');
const path = require('path');
const fs = require('fs');

const ALLOWED_EXTERNAL_PROTOCOLS = new Set(['https:']);

function isSafeExternalUrl(rawUrl) {
  try {
    const parsed = new URL(rawUrl);
    return ALLOWED_EXTERNAL_PROTOCOLS.has(parsed.protocol);
  } catch {
    return false;
  }
}

const ELECTRON_SECURITY_PREFERENCES = Object.freeze({
  nodeIntegration: false,
  contextIsolation: true,
  sandbox: true,
  webSecurity: true,
  allowRunningInsecureContent: false,
  enableRemoteModule: false,
  preload: path.join(__dirname, 'preload.js')
});

function createWindow() {
  const distIndex = path.join(__dirname, '..', 'dist', 'index.html');
  if (!fs.existsSync(distIndex)) {
    throw new Error(`Production frontend build not found at ${distIndex}. Run "npm run build" first.`);
  }

  const win = new BrowserWindow({
    width: 1360,
    height: 880,
    minWidth: 960,
    minHeight: 640,
    autoHideMenuBar: true,
    backgroundColor: '#0a0a12',
    title: 'Linacre LLM Hub',
    webPreferences: ELECTRON_SECURITY_PREFERENCES
  });

  // Enforce strict CSP on local responses
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http://127.0.0.1:11434 http://localhost:11434; font-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none';"
        ]
      }
    });
  });

  // Restrict navigation away from the bundled app
  win.webContents.on('will-navigate', (event, navigationUrl) => {
    const currentOrigin = new URL(win.webContents.getURL()).origin;
    try {
      const target = new URL(navigationUrl);
      if (target.origin !== currentOrigin) {
        event.preventDefault();
        if (isSafeExternalUrl(navigationUrl)) {
          shell.openExternal(navigationUrl);
        }
      }
    } catch {
      event.preventDefault();
    }
  });

  // Open safe https:// links in OS browser; deny everything else
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (isSafeExternalUrl(url)) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  win.loadFile(distIndex);
  return win;
}

if (typeof ipcMain !== 'undefined' && ipcMain && typeof ipcMain.handle === 'function') {
  ipcMain.handle('app:get-info', () => ({
    name: app.getName(),
    version: app.getVersion(),
    platform: process.platform
  }));

  ipcMain.handle('app:open-external', (_event, url) => {
    if (typeof url === 'string' && isSafeExternalUrl(url)) {
      return shell.openExternal(url);
    }
    return false;
  });
}

if (typeof app !== 'undefined' && app && typeof app.whenReady === 'function') {
  app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
}

module.exports = {
  ELECTRON_SECURITY_PREFERENCES,
  isSafeExternalUrl,
  createWindow
};
