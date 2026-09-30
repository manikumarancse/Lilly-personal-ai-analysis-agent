class ChartAnalyzer:
    """Deterministic analysis of the current Lilly price-observation session."""

    def analyze(self, history):
        session = history.current_session
        if not session:
            return {"ready": False, "message": "No monitoring session is active."}

        items = [x for x in history.recent(1000, session.get("id")) if x.get("type") == "price"]
        if len(items) < 2:
            return {
                "ready": False,
                "message": "Lilly needs at least 2 price observations in the current session.",
                "observations": len(items),
                "session": session,
            }

        values = [float(x["value"]) for x in items]
        first, latest = values[0], values[-1]
        high, low = max(values), min(values)
        change = latest - first
        change_pct = (change / first * 100.0) if first else None
        price_range = high - low
        range_position = ((latest - low) / price_range * 100.0) if price_range else 50.0

        if change > 0:
            direction = "up"
        elif change < 0:
            direction = "down"
        else:
            direction = "flat"

        recent = values[-min(5, len(values)):]
        recent_change = recent[-1] - recent[0]
        if recent_change > 0:
            momentum = "rising"
        elif recent_change < 0:
            momentum = "falling"
        else:
            momentum = "flat"

        if range_position >= 75:
            location = "near session high"
        elif range_position <= 25:
            location = "near session low"
        else:
            location = "mid session range"

        return {
            "ready": True,
            "session": session,
            "observations": len(values),
            "first": first,
            "latest": latest,
            "high": high,
            "low": low,
            "range": price_range,
            "change": change,
            "change_pct": change_pct,
            "direction": direction,
            "momentum": momentum,
            "range_position_pct": range_position,
            "location": location,
            "from": items[0].get("observed_at"),
            "to": items[-1].get("observed_at"),
            "basis": "current_session_price_observations",
        }
