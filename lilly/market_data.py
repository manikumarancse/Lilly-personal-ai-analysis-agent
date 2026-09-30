import json
import threading
from datetime import datetime
from pathlib import Path


class CandleStore:
    def __init__(self, data_dir="data", max_candles=500):
        self.path = Path(data_dir) / "candles.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_candles = max_candles
        self._lock = threading.Lock()
        self._context = {"symbol": None, "timeframe": None, "updated_at": None}
        self._candles = []

    @property
    def context(self):
        with self._lock:
            return dict(self._context)

    def set_context(self, symbol=None, timeframe=None):
        with self._lock:
            changed = symbol != self._context.get("symbol") or timeframe != self._context.get("timeframe")
            self._context = {
                "symbol": symbol or None,
                "timeframe": timeframe or None,
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            if changed:
                self._candles = []
            self._persist()
            return dict(self._context), changed

    def replace(self, candles):
        clean = []
        for item in candles[-self.max_candles:]:
            clean.append({
                "time": item.get("time"),
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item["volume"]) if item.get("volume") is not None else None,
            })
        with self._lock:
            self._candles = clean
            self._persist()
        return len(clean)

    def list(self):
        with self._lock:
            return [dict(x) for x in self._candles]

    def _persist(self):
        self.path.write_text(json.dumps({"context": self._context, "candles": self._candles}, indent=2), encoding="utf-8")


class MarketStructureAnalyzer:
    def analyze(self, store):
        candles = store.list()
        context = store.context
        if len(candles) < 3:
            return {
                "ready": False,
                "message": "Lilly needs at least 3 structured OHLC candles.",
                "candles": len(candles),
                "context": context,
            }

        highs = [x["high"] for x in candles]
        lows = [x["low"] for x in candles]
        closes = [x["close"] for x in candles]
        higher_highs = sum(1 for a, b in zip(highs, highs[1:]) if b > a)
        lower_highs = sum(1 for a, b in zip(highs, highs[1:]) if b < a)
        higher_lows = sum(1 for a, b in zip(lows, lows[1:]) if b > a)
        lower_lows = sum(1 for a, b in zip(lows, lows[1:]) if b < a)

        if higher_highs > lower_highs and higher_lows > lower_lows:
            structure = "bullish"
        elif lower_highs > higher_highs and lower_lows > higher_lows:
            structure = "bearish"
        else:
            structure = "mixed"

        lookback = candles[-min(20, len(candles)):]
        support = min(x["low"] for x in lookback)
        resistance = max(x["high"] for x in lookback)
        bullish = sum(1 for x in candles if x["close"] > x["open"])
        bearish = sum(1 for x in candles if x["close"] < x["open"])

        return {
            "ready": True,
            "context": context,
            "candles": len(candles),
            "structure": structure,
            "support": support,
            "resistance": resistance,
            "latest_close": closes[-1],
            "higher_highs": higher_highs,
            "lower_highs": lower_highs,
            "higher_lows": higher_lows,
            "lower_lows": lower_lows,
            "bullish_candles": bullish,
            "bearish_candles": bearish,
            "basis": "structured_ohlc_candles",
        }
