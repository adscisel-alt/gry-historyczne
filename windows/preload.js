const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('electronAPI', { zamknij: () => ipcRenderer.send('zamknij') });
