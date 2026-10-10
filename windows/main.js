// Okno Windows dla gry „Damian Ściseł i Kapelusz Szyfrów”.
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function utworzOkno() {
  const okno = new BrowserWindow({
    width: 1280,
    height: 760,
    minWidth: 960,
    minHeight: 560,
    title: 'Damian Ściseł i Kapelusz Szyfrów',
    backgroundColor: '#0b0714',
    autoHideMenuBar: true,
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });
  okno.setMenu(null);
  okno.webContents.on('before-input-event', (e, wej) => {
    if (wej.type !== 'keyDown') return;
    if (wej.key === 'F11') { okno.setFullScreen(!okno.isFullScreen()); e.preventDefault(); }
    if (wej.key === 'Escape' && okno.isFullScreen()) okno.setFullScreen(false);
  });
  okno.loadFile(path.join(__dirname, 'gra', 'index.html'));
}

ipcMain.on('zamknij', () => app.quit());
app.whenReady().then(utworzOkno);
app.on('window-all-closed', () => app.quit());
