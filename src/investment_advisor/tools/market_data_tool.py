import json
import re
from datetime import datetime, timezone

import yfinance as yf
from crewai.tools import BaseTool


class MarketDataTool(BaseTool):
    """Fetches structured equity market data via yfinance."""

    name: str = "market_data_tool"
    description: str = (
        "Use this tool to fetch the latest market snapshot for a given equity ticker. "
        "It returns the latest close, day-over-day delta, short-term trend, recent "
        "historical prices, and volatility statistics in JSON format."
    )

    _ticker_pattern = re.compile(r"^[A-Za-z0-9.\-]{1,10}$")

    def _normalize_ticker(self, ticker: str) -> str:
        candidate = (ticker or "").strip().upper()
        if not candidate or not self._ticker_pattern.match(candidate):
            raise ValueError("Provide a valid stock ticker symbol (e.g., AAPL, MSFT, BRK.B).")
        return candidate

    def _run(self, ticker: str) -> str:
        symbol = self._normalize_ticker(ticker)
        try:
            instrument = yf.Ticker(symbol)
            history = instrument.history(period="1mo", interval="1d")
        except Exception as exc:  # pragma: no cover - yfinance raises generic exceptions
            raise ValueError(f"Unable to fetch data for {symbol}: {exc}") from exc

        if history.empty or len(history.index) < 2:
            raise ValueError(f"Not enough market data returned for {symbol}.")

        close_series = history["Close"].dropna()
        last_close = float(close_series.iloc[-1])
        prev_close = float(close_series.iloc[-2])
        delta = last_close - prev_close
        delta_pct = (delta / prev_close * 100) if prev_close else 0.0

        trailing_window = close_series.tail(5)
        sma_5 = float(trailing_window.mean())
        price_direction = "Bullish" if last_close > sma_5 else "Bearish"
        if abs(delta_pct) <= 0.25:
            price_direction = "Sideways"

        returns = close_series.pct_change().dropna()
        annualized_vol = float(returns.std() * (252 ** 0.5)) if not returns.empty else 0.0

        payload = {
            "stock": symbol,
            "price": round(last_close, 2),
            "daily_change": round(delta, 2),
            "daily_change_pct": round(delta_pct, 2),
            "trend": price_direction,
            "moving_average_5d": round(sma_5, 2),
            "high_30d": round(float(close_series.max()), 2),
            "low_30d": round(float(close_series.min()), 2),
            "volatility": round(annualized_vol, 4),
            "price_series": [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "close": round(float(value), 2),
                }
                for idx, value in close_series.tail(10).items()
            ],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(payload)
