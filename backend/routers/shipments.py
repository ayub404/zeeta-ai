"""
Zeeta — routers/shipments.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Shipment, User
from schemas import ShipmentOut, ShipmentUpdate
from auth_utils import get_current_user
from services.weather import get_weather_cache

router = APIRouter()


@router.get("", response_model=list[ShipmentOut])
async def get_shipments(
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    result = await db.execute(
        select(Shipment).order_by(Shipment.risk_score.desc())
    )
    shipments = result.scalars().all()

    # Enrich risk scores with live weather
    weather = get_weather_cache()
    for s in shipments:
        bonus = 0
        for port in [s.origin, s.destination]:
            w = weather.get(port, {})
            if w.get("risk") == "high":   bonus += 15
            elif w.get("risk") == "medium": bonus += 7
        s.risk_score = min(s.risk_score + bonus, 100)

    return shipments


@router.get("/{shipment_id}", response_model=ShipmentOut)
async def get_shipment(
    shipment_id: str,
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    s = await db.get(Shipment, shipment_id)
    if not s:
        raise HTTPException(404, "Shipment not found")
    return s


@router.patch("/{shipment_id}", response_model=ShipmentOut)
async def update_shipment(
    shipment_id: str,
    body: ShipmentUpdate,
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    s = await db.get(Shipment, shipment_id)
    if not s:
        raise HTTPException(404, "Shipment not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(s, k, v)
    await db.commit()
    return s
