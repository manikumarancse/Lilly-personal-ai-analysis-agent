# Project Lilly

## Current version: 0.7.0 — Observation history + What's the update?

Lilly now persists automatic price observations locally and can summarize what happened while the chart was being watched.

### New
- `data/observations.jsonl` local observation history
- Timestamp, price, source and selected-tab context per observation
- `GET /observations?limit=100`
- `GET /update`
- **What's the update?** button in the Chrome extension
- Update includes latest price, observed high/low, change over the returned history window, observation count, active tasks and triggered tasks
- Existing Step 5 condition/notification behavior remains unchanged

### Update/test
```powershell
git pull origin main
.\.venv\Scripts\Activate.ps1
python run_lilly.py
```
Then open `chrome://extensions` and Reload Lilly.

Open TradingView, start watching the tab, let observations accumulate, then click **What's the update?**.

## Roadmap
1. Persistent notifications — completed
2. Windows background/tray — completed
3. Explicit Chrome tab connection — completed
4. Chart capture — completed
5. Task/condition engine — completed
6. Automatic TradingView live-price adapter — completed
7. Observation history + "What's the update?" — completed
8. Start automatically with Windows
