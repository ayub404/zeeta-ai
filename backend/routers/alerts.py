"""
Zeeta — routers/alerts.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from database import get_db
from models import Alert, Severity, User
from schemas import AlertOut
from auth_utils import get_current_user
from services.live_data import get_live_alerts

router = APIRouter()

SEV_ORDER = {Severity.high: 0, Severity.medium: 1, Severity.low: 2}


@router.get("", response_model=list[AlertOut])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    # Get DB alerts (static/port)
    result = await db.execute(
        select(Alert).where(Alert.is_active == True)
    )
    db_alerts = list(result.scalars().all())

    # Merge with live weather + geo alerts
    live = await get_live_alerts(db)
    all_alerts = db_alerts + live

    return sorted(all_alerts, key=lambda a: SEV_ORDER.get(a.severity, 3))


@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    _:  User = Depends(get_current_user),
):
    a = await db.get(Alert, alert_id)
    if not a:
        raise HTTPException(404, "Alert not found")
    a.is_active   = False
    a.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": f"Alert {alert_id} resolved"}
