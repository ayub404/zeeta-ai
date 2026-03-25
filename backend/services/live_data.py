"""
Zeeta — services/live_data.py
Fetches geopolitical alerts from GDELT and converts weather cache to Alert objects.
"""

import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from models import Alert, AlertType, Severity
from services.weather import get_weather_cache, PORTS


async def get_live_alerts(db: AsyncSession) -> list[Alert]:
    weather_alerts = _build_weather_alerts()
    geo_alerts     = await _fetch_geo_alerts()
    return weather_alerts + geo_alerts


def _build_weather_alerts() -> list[Alert]:
    cache  = get_weather_cache()
    alerts = []
    now    = datetime.now(timezone.utc).strftime("%H:%M UTC")

    for i, (port, data) in enumerate(cache.items()):
        if not data.get("alert_msg") or data.get("risk") not in ("high", "medium"):
            continue
        sev = Severity.high if data["risk"] == "high" else Severity.medium
        alerts.append(Alert(
            id=f"WX-{port[:3].upper()}-LIVE",
            type=AlertType.weather,
            severity=sev,
            message=f"{port}: {data['alert_msg']}",
            affected_shipments=2,
            source="Open-Meteo",
            port=port,
            region=data.get("region"),
            wind_kmh=data.get("wind"),
            wave_height_m=data.get("wave"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ))

    return alerts


async def _fetch_geo_alerts() -> list[Alert]:
    alerts = []
    try:
        url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
            "?query=shipping+port+OR+trade+sanctions+OR+strait+blockade"
            "&mode=artlist&maxrecords=5&sort=hybridrel&format=json&timespan=1440"
        )
        async with httpx.AsyncClient(timeout=12) as client:
            resp = await client.get(url)
            data = resp.json()

        seen = set()
        for i, art in enumerate(data.get("articles", [])[:4]):
            title = art.get("title", "").strip()
            if not title or title in seen:
                continue
            seen.add(title)
            tl  = title.lower()
            sev = (
                Severity.high   if any(w in tl for w in ["crisis", "conflict", "blockade", "war", "sanction"])
                else Severity.medium if any(w in tl for w in ["disruption", "delay", "restriction", "tension"])
                else Severity.low
            )
            alerts.append(Alert(
                id=f"GEO-{i}-LIVE",
                type=AlertType.geopolitical,
                severity=sev,
                message=title[:200],
                affected_shipments=1,
                source="GDELT",
                is_active=True,
                created_at=datetime.now(timezone.utc),
            ))
    except Exception as e:
        print(f"[GDELT] Failed: {e}")

    return alerts
