"""Utilities for sending AI Investment Advisor reports via WhatsApp."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class WhatsAppDeliveryError(RuntimeError):
    """Raised when the WhatsApp delivery pipeline cannot be completed."""


def _coerce_report_dict(report: Any) -> Dict[str, Any]:
    """Attempt to convert a CrewAI result into a dictionary for formatting."""
    if isinstance(report, dict):
        return report

    if isinstance(report, str):
        try:
            parsed = json.loads(report)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"raw": report}

    raw = getattr(report, "raw", None)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return {"raw": str(report)}


def format_report_for_whatsapp(report: Any) -> str:
    """Convert the structured CrewAI report into a WhatsApp-friendly string."""
    data = _coerce_report_dict(report)

    stock = str(data.get("stock", "Unknown"))
    price = data.get("price", "N/A")
    trend = data.get("trend", "N/A")
    sentiment = data.get("sentiment", data.get("dominant_sentiment", "N/A"))
    risk = data.get("risk", "N/A")
    summary = data.get("summary") or data.get("analysis") or data.get("raw") or "Summary unavailable."
    recommendation = str(data.get("recommendation", "N/A")).upper()

    lines = [
        f"📊 STOCK REPORT ({stock})",
        "",
        f"💰 Price: {price}",
        f"📈 Trend: {trend}",
        f"📰 Sentiment: {sentiment}",
        f"⚠️ Risk: {risk}",
        "",
        "🧠 Summary:",
        "",
        summary.strip(),
        "",
        f"✅ Recommendation: {recommendation}",
    ]
    return "\n".join(lines)


def _get_env_setting(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise WhatsAppDeliveryError(
            f"Missing required environment variable '{key}' for WhatsApp delivery."
        )
    return value


def _ensure_prefixed(number: str) -> str:
    if number.startswith("whatsapp:"):
        return number
    return f"whatsapp:{number}"


def send_whatsapp_message(message: str) -> None:
    """Send the supplied message through WhatsApp using Twilio's REST API."""
    account_sid = _get_env_setting("TWILIO_ACCOUNT_SID")
    auth_token = _get_env_setting("TWILIO_AUTH_TOKEN")
    from_number = _ensure_prefixed(_get_env_setting("TWILIO_WHATSAPP_FROM"))
    to_number = _ensure_prefixed(_get_env_setting("TWILIO_WHATSAPP_TO"))

    client = Client(account_sid, auth_token)

    try:
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number,
        )
    except TwilioRestException as exc:
        detail = exc.msg or str(exc)
        raise WhatsAppDeliveryError(f"Twilio API error: {detail}") from exc
