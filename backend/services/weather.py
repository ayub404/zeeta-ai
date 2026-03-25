"""
Zeeta — services/weather.py
Fetches live weather for key shipping ports via Open-Meteo (free, no key).
"""

import asyncio
import httpx
from datetime import datetime, timezone

PORTS = {
    "Shanghai":    {"lat": 31.23,  "lon": 121.47, "region": "Asia-Pacific"},
    "Rotterdam":   {"lat": 51.92,  "lon": 4.48,   "region": "Europe"},
    "Singapore":   {"lat": 1.29,   "lon": 103.85, "region": "Asia-Pacific"},
    "Los Angeles": {"lat": 33.73,  "lon": -118.26,"region": "North America"},
    "Dubai":       {"lat": 25.20,  "lon": 55.27,  "region": "Middle East"},
    "Hamburg":     {"lat": 53.55,  "lon": 9.99,   "region": "Europe"},
    "Busan":       {"lat": 35.10,  "lon": 129.04, "region": "Asia-Pacific"},
    "Long Beach":  {"lat": 33.75,  "lon": -118.19,"region": "North America"},
}

# In-memory cache: { "Shanghai": { risk, wind, wave, region } }
_weather_cache: dict = {}
_last_refresh: datetime | None = None


def get_weather_cache() -> dict:
    return _weather_cache


def _classify(wind: float, wave: float) -> tuple[str, str | None]:
    if wind >= 75 or wave >= 4.0:
        return "high", f"Severe — winds {wind:.0f} km/h, waves {wave:.1f}m. Delays 2–4 days."
    if wind >= 50 or wave >= 2.5:
        return "medium", f"Rough seas — winds {wind:.0f} km/h. Monitor closely."
    if wind >= 30:
        return "low", None
    return "clear", None


async def refresh_weather():
    global _last_refresh
    async with httpx.AsyncClient(timeout=12) as client:
        port_names = list(PORTS.keys())
        tasks = [
            client.get(
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={c['lat']}&longitude={c['lon']}"
                f"&current=temperature_2m,windspeed_10m"
                f"&hourly=wave_height&forecast_days=1"
            )
            for c in PORTS.values()
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for port, resp in zip(port_names, responses):
        coords = PORTS[port]
        try:
            if isinstance(resp, Exception):
                raise resp
            d    = resp.json()
            cur  = d.get("current", {})
            wind = float(cur.get("windspeed_10m", 0))
            raw_waves = d.get("hourly", {}).get("wave_height", [0])
            wave = max((w for w in raw_waves[:6] if w is not None), default=0.0)
            risk, alert_msg = _classify(wind, wave)

            _weather_cache[port] = {
                "risk":      risk,
                "wind":      round(wind, 1),
                "wave":      round(wave, 2),
                "region":    coords["region"],
                "alert_msg": alert_msg,
            }
        except Exception as e:
            _weather_cache[port] = {
                "risk": "unknown", "wind": 0, "wave": 0,
                "region": coords["region"], "alert_msg": None,
            }
            print(f"[Weather] Failed for {port}: {e}")

    _last_refresh = datetime.now(timezone.utc)
    print(f"[Zeeta] Weather refreshed at {_last_refresh.isoformat()}")
