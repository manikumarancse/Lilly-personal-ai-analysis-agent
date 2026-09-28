# Project Lilly

Personal AI analysis assistant for Windows.

## Current version: 0.2.0 — Step 2

Completed:
- Persistent bottom-right desktop alerts
- Alert sound
- Alerts remain until acknowledged
- Always-on-top notification window
- Windows background process
- System-tray icon
- Active / Paused status
- Test alert
- Explicit Exit control

## Run

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_lilly.py
```

Lilly stays active in the Windows system tray. Right-click the **L** icon to test alerts, view status, pause monitoring, or exit.

## Roadmap

1. Persistent notification engine — completed
2. Windows background process/system tray — completed
3. Chrome extension + explicit tab permission — next
4. Chart capture/data adapter
5. Task manager ("watch this level")
6. Observation history
7. "Lilly, what's the update?"
8. Start automatically with Windows

## Core rule

Notifications are a first-class feature. Important Lilly alerts must appear above the user's current work, make a sound, and remain visible until explicitly acknowledged.
