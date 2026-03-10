import json
import os
from datetime import datetime
from typing import List, Tuple

import requests
from crewai.tools import BaseTool


class NewsSentimentTool(BaseTool):
    """Fetches recent news via NewsAPI and performs a light sentiment tally."""

    name: str = "news_sentiment_tool"
    description: str = (
        "Use this tool to pull the latest financial news for a ticker using NewsAPI and "
        "receive aggregated sentiment (positive/negative/neutral) with representative "
        "headlines."
    )

    def _get_api_key(self) -> str:
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            raise ValueError("Set NEWSAPI_KEY in the environment to use NewsAPI.")
        return api_key

    def _fetch_articles(self, ticker: str) -> List[dict]:
        params = {
            "q": ticker,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 8,
            "apiKey": self._get_api_key(),
        }
        response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"NewsAPI error ({response.status_code}): {response.text}")
        payload = response.json()
        return payload.get("articles", [])

    def _score_headline(self, text: str) -> Tuple[str, float]:
        lowered = text.lower()
        positive_tokens = ["beat", "growth", "upside", "record", "surge"]
        negative_tokens = ["slump", "miss", "lawsuit", "fraud", "loss", "downturn"]
        pos_score = sum(token in lowered for token in positive_tokens)
        neg_score = sum(token in lowered for token in negative_tokens)
        if pos_score > neg_score:
            return "positive", pos_score
        if neg_score > pos_score:
            return "negative", -neg_score
        return "neutral", 0.0

    def _run(self, ticker: str) -> str:
        articles = self._fetch_articles(ticker)
        summaries = []
        totals = {"positive": 0, "negative": 0, "neutral": 0}

        for article in articles:
            headline = article.get("title") or article.get("description") or ""
            if not headline:
                continue
            sentiment, score = self._score_headline(headline)
            totals[sentiment] += 1
            summaries.append(
                {
                    "headline": headline[:180],
                    "url": article.get("url"),
                    "sentiment": sentiment,
                    "published_at": article.get("publishedAt"),
                    "score": score,
                }
            )

        dominant = max(totals, key=totals.get)
        payload = {
            "stock": ticker.upper(),
            "sentiment_counts": totals,
            "dominant_sentiment": dominant,
            "articles": summaries,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }
        return json.dumps(payload)
