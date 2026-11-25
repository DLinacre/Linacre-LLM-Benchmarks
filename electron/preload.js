const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('linacreDesktop', Object.freeze({
  getAppInfo: () => ipcRenderer.invoke('app:get-info'),
  openExternal: (url) => {
    if (typeof url !== 'string' || !url.startsWith('https://')) {
      return Promise.resolve(false);
    }
    return ipcRenderer.invoke('app:open-external', url);
  }
}));
