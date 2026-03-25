"""
Zeeta — routers/decisions.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from database import get_db
from models import Decision, Shipment, User
from schemas import DecisionOut, DecisionApply
from auth_utils import get_current_user
from services.weather import get_weather_cache

router = APIRouter()

# Decision templates — in production, replace with real ML model
TEMPLATES = {
    "ZT-001": ("Reroute via Suez Canal",
                "Typhoon risk on current route. Suez adds 800nm but saves 4 days net.",
                "+$2,400", "-4 days", 91),
    "ZT-002": ("Split — 30% air, 70% sea",
                "Client deadline Dec 20, sea ETA Dec 22. Air covers critical portion.",
                "+$8,100", "-2 days", 84),
    "ZT-005": ("Split shipment 60/40",
                "Port congestion at Long Beach adds 5 days. Partial air mitigates cost.",
                "+$5,600", "-3 days", 78),
}


@router.post("/{shipment_id}", response_model=DecisionOut, status_code=201)
async def create_decision(
    shipment_id: str,
    db:  AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = await db.get(Shipment, shipment_id)
    if not s:
        raise HTTPException(404, "Shipment not found")

    # Build live weather context string
    weather = get_weather_cache()
    ctx = ""
    for port in [s.origin, s.destination]:
        w = weather.get(port, {})
        if w.get("risk") in ("high", "medium"):
            ctx += f" Live: {port} winds {w.get('wind', 0):.0f} km/h."

    action, reason, cost, time_imp, conf = TEMPLATES.get(
        shipment_id,
        ("No action required",
         f"Shipment is on track with acceptable risk.{ctx}",
         "$0", "0 days", 95)
    )

    decision = Decision(
        shipment_id=shipment_id,
        user_id=current_user.id,
        action=action,
        reason=reason + ctx,
        cost_impact=cost,
        time_impact=time_imp,
        confidence=conf,
        weather_context=str(weather.get(s.origin, {})),
    )
    db.add(decision)
    await db.commit()
    return decision


@router.get("/{shipment_id}", response_model=list[DecisionOut])
async def get_decisions(
    shipment_id: str,
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    result = await db.execute(
        select(Decision)
        .where(Decision.shipment_id == shipment_id)
        .order_by(Decision.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{decision_id}/apply", response_model=DecisionOut)
async def apply_decision(
    decision_id: int,
    body: DecisionApply,
    db:  AsyncSession = Depends(get_db),
    _:   User = Depends(get_current_user),
):
    d = await db.get(Decision, decision_id)
    if not d:
        raise HTTPException(404, "Decision not found")
    d.was_applied = True
    d.applied_at  = datetime.now(timezone.utc)
    d.outcome     = body.outcome
    await db.commit()
    return d
