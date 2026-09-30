# Project Lilly

## Current version: 0.8.0 — Session-based chart monitoring

Lilly now separates observations into monitoring sessions. Historical observations stay saved, but old timeframe or symbol values no longer enter the current update summary.

### New
- Watching a tab starts a fresh session.
- Every new price observation gets a session ID.
- **What's the update?** summarizes only the current session.
- Triggered count is limited to tasks triggered during the current session.
- **Start New Session** resets the current summary after a timeframe or symbol change without deleting history.
- Existing condition alerts remain intact.

### Update and test

```powershell
git pull origin main
.\.venv\Scripts\Activate.ps1
python run_lilly.py
```

Reload Lilly in `chrome://extensions`. Start watching TradingView. When you change timeframe or symbol, click **Start New Session**, wait for new observations, then click **What's the update?**.

Automatic detection of TradingView timeframe and symbol changes is a later enhancement.
