# Project Lilly — V1

Current milestone: **Persistent Desktop Notification Engine**

## Behavior
- Appears in the bottom-right corner.
- Always stays above normal application windows.
- Plays a Windows alert sound.
- Does **not** auto-dismiss.
- Remains until the user clicks **Acknowledge**.
- Designed to work while the user is in Chrome, Excel, VS Code, etc.

## Run on Windows

Open PowerShell inside this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_lilly.py
```

You should see a Lilly alert in the bottom-right after startup.

## V1 build order
1. Persistent notification engine — started
2. Lilly background process/system tray
3. Chrome extension + explicit tab permission
4. Chart capture/data adapter
5. Task manager ("watch this level")
6. Observation history
7. "Lilly, what's the update?"
8. Start automatically with Windows

The notification engine is intentionally independent from chart analysis so every future Lilly module can trigger the same persistent alert.
