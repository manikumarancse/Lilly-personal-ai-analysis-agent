# Project Lilly

Personal AI analysis assistant for Windows.

## Current version: 0.4.0 — Step 4

### Completed

- Persistent desktop alerts with sound and acknowledgement
- Windows background process + system tray
- Explicit Chrome **Watch This Tab / Stop Watching**
- Local-only bridge on `127.0.0.1:8765`
- Visible-tab chart screenshot capture
- **Capture Chart Now** control
- Capture validation: images are accepted only from the selected tab
- Latest chart image stored locally at `data/captures/latest_chart.jpg`
- Latest capture metadata stored at `data/captures/latest_chart.json`
- Tray/status reports the latest capture timestamp

Step 4 creates the chart visual-data pipeline. It does not place trades or make autonomous trading decisions.

## Update and run

```powershell
git pull origin main
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_lilly.py
```

## Reload the Chrome extension after this update

1. Open `chrome://extensions`
2. Find **Lilly — Personal AI Analysis Agent**
3. Click **Reload**
4. Open your chart tab
5. Open Lilly and click **Watch This Tab**
6. Click **Capture Chart Now**
7. Check `data/captures/latest_chart.jpg`

The watched tab must be the visible/active tab at capture time because Chrome's visible-tab capture API captures what is currently rendered.

## Roadmap

1. Persistent notification engine — completed
2. Windows background process/system tray — completed
3. Chrome extension + explicit tab permission — completed
4. Chart capture/data adapter — completed
5. Task/analysis engine ("watch this level", chart conditions)
6. Observation history
7. "Lilly, what's the update?"
8. Start automatically with Windows
