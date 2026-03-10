import json
from statistics import mean, pstdev
from typing import Dict, List

from crewai.tools import BaseTool


class RiskAnalyzerTool(BaseTool):
    """Condenses quantitative metrics into a Low/Medium/High risk score."""

    name: str = "risk_analyzer_tool"
    description: str = (
        "Consumes a JSON payload containing price_series, volatility, and sentiment to "
        "determine a qualitative risk level along with rationale."
    )

    def _compute_trend_strength(self, series: List[Dict[str, float]]) -> float:
        values = [point["close"] for point in series]
        if len(values) < 3:
            return 0.0
        first_half = mean(values[: len(values) // 2])
        second_half = mean(values[len(values) // 2 :])
        return (second_half - first_half) / (first_half or 1)

    def _run(self, market_snapshot_json: str) -> str:
        data = json.loads(market_snapshot_json)
        price_series = data.get("price_series", [])
        volatility = float(data.get("volatility", 0))
        sentiment = data.get("sentiment", "neutral")

        if not price_series:
            raise ValueError("Risk analysis requires at least one price observation.")

        returns = []
        for idx in range(1, len(price_series)):
            prev = price_series[idx - 1]["close"]
            curr = price_series[idx]["close"]
            if prev:
                returns.append((curr - prev) / prev)

        realized_vol = pstdev(returns) if len(returns) > 1 else 0.0
        realized_vol_annualized = realized_vol * (252 ** 0.5)
        trend_strength = self._compute_trend_strength(price_series)

        risk_score = 0
        if volatility > 0.4 or realized_vol_annualized > 0.5:
            risk_score += 2
        elif volatility > 0.25:
            risk_score += 1

        if trend_strength < -0.03:
            risk_score += 2
        elif trend_strength < 0:
            risk_score += 1

        sentiment_penalty = {"negative": 2, "neutral": 1, "positive": 0}
        risk_score += sentiment_penalty.get(sentiment, 1)

        if risk_score <= 1:
            label = "Low"
        elif risk_score <= 3:
            label = "Medium"
        else:
            label = "High"

        payload = {
            "stock": data.get("stock"),
            "volatility": round(volatility, 4),
            "realized_vol": round(realized_vol_annualized, 4),
            "trend_strength": round(trend_strength, 4),
            "sentiment": sentiment,
            "risk_level": label,
            "explanation": (
                "Risk reflects volatility, price momentum, and sentiment. "
                "Ensure allocations match portfolio tolerance."
            ),
        }
        return json.dumps(payload)
