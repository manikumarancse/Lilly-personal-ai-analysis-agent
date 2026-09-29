# Project Lilly

Personal AI analysis assistant for Windows.

## Current version: 0.3.0 — Step 3

### Completed

- Persistent bottom-right desktop alerts with sound
- Alerts remain until acknowledged
- Windows background process + system tray
- Active / Paused state
- Local Chrome bridge on `127.0.0.1:8765`
- Chrome Manifest V3 extension
- Explicit **Watch This Tab**
- Explicit **Stop Watching**
- Selected tab title/URL passed to Lilly
- Tray displays Chrome watch state
- Persistent alert confirms watch start/stop

Step 3 intentionally tracks only the tab the user selects. It does **not** yet capture or analyze chart pixels/data; that is Step 4.

## Run Lilly

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_lilly.py
```

## Install the Chrome extension (once)

1. Open Chrome and go to `chrome://extensions`
2. Turn on **Developer mode**
3. Click **Load unpacked**
4. Select the project's `chrome-extension` folder
5. Pin **Lilly — Personal AI Analysis Agent** to the Chrome toolbar

## Test Step 3

1. Keep `python run_lilly.py` running.
2. Open the Chrome tab you want Lilly to watch.
3. Click the Lilly extension.
4. It should show **Lilly connected**.
5. Click **Watch This Tab**.
6. Lilly should produce a persistent desktop alert and the tray should say it is watching Chrome.
7. Click **Stop Watching** to end the explicit watch.

## Roadmap

1. Persistent notification engine — completed
2. Windows background process/system tray — completed
3. Chrome extension + explicit tab permission — completed
4. Chart capture/data adapter — next
5. Task manager ("watch this level")
6. Observation history
7. "Lilly, what's the update?"
8. Start automatically with Windows
