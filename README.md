# Project Lilly

Personal AI analysis assistant for Windows.

## Current version: 0.6.0 — Automatic TradingView live-price monitoring

### New
- Background Chrome service worker
- Automatic price observation from the explicitly selected TradingView tab
- DOM-based TradingView current/close price extraction every ~2 seconds
- Observations automatically feed Lilly's Step 5 task engine
- Persistent sound alert when an active >= / <= condition triggers
- Live price shown in Chrome popup and Windows tray
- Selected-tab validation remains in the local Lilly bridge
- No broker credentials and no trade execution

### Update
```powershell
git pull origin main
python run_lilly.py
```
Then open `chrome://extensions` and click **Reload** on Lilly. Because the extension permissions changed, Chrome may ask you to approve the updated permissions.

### Test
1. Open a TradingView chart.
2. Lilly -> **Watch This Tab + Start Live Monitor**.
3. Confirm **Automatic live price** begins showing a changing value.
4. Add a condition close to the current price.
5. Leave Lilly running. The Chrome popup may be closed; the background worker continues polling the selected TradingView tab.
6. When the observed value reaches the condition, Lilly fires the persistent Windows alert.

### Reliability note
This adapter reads TradingView's rendered DOM. TradingView can change its internal markup, so Lilly treats this as an adapter rather than a guaranteed market-data feed. The task engine remains independent so a structured data source can replace/supplement it later.

## Roadmap
1. Persistent notifications — completed
2. Windows background/tray — completed
3. Explicit Chrome tab connection — completed
4. Chart capture — completed
5. Task/condition engine — completed
6. Automatic TradingView live-price adapter — completed
7. Observation history + "Lilly, what's the update?"
8. Start automatically with Windows
