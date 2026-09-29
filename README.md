# Project Lilly

Personal AI analysis assistant for Windows.

## Current version: 0.5.0 — Step 5

Step 5 adds Lilly's persistent chart-task/condition engine.

### New in Step 5
- Persistent watch tasks stored in `data/tasks.json`
- Price reaches/goes above a level
- Price reaches/goes below a level
- Optional task labels
- Active/triggered task state
- Persistent Lilly alert when a condition is triggered
- Task count in the Windows tray
- Chrome popup task creation/deletion UI
- Manual **Test observation** input to validate the engine end-to-end

### Important architecture boundary
Step 4 gives Lilly chart screenshots, but exact numeric price extraction from arbitrary chart pixels is not yet reliable. Step 5 therefore separates **observation input** from **condition evaluation** instead of pretending screenshots provide exact prices.

The manual test observation proves:
`observation -> task engine -> condition evaluation -> persistent alert`.

A later structured market-data or AI chart-analysis adapter can feed this same engine automatically.

## Update/test
```powershell
git pull origin main
python run_lilly.py
```

Then open `chrome://extensions` and **Reload** Lilly.

Test:
1. Watch your chart tab.
2. Add a task such as **Price reaches/goes above 100**.
3. Under **Test observation**, enter `99` — no condition alert should fire.
4. Enter `100` or `101` — Lilly should fire a persistent **Chart Condition Triggered** alert.
5. The task should become **TRIGGERED** and no longer be active.

## Roadmap
1. Persistent notification engine — completed
2. Windows background process/system tray — completed
3. Chrome extension + explicit tab permission — completed
4. Chart capture/data adapter — completed
5. Task/condition engine — completed
6. Observation history + automatic analysis/data adapter
7. "Lilly, what's the update?"
8. Start automatically with Windows
