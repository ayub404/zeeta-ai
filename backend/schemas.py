"""
Zeeta — schemas.py
Pydantic request/response models.
"""

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from models import ShipmentStatus, AlertType, Severity, UserRole


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email:     str
    full_name: str
    password:  str
    company:   Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_must_have_at(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return v.lower().strip()


class LoginRequest(BaseModel):
    email:    str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user_id:      str
    email:        str
    role:         str
    full_name:    str


class UserOut(BaseModel):
    id:         str
    email:      str
    full_name:  str
    role:       UserRole
    company:    Optional[str]
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Shipments ─────────────────────────────────────────────────────────────────

class ShipmentOut(BaseModel):
    id:             str
    origin:         str
    destination:    str
    carrier:        str
    status:         ShipmentStatus
    risk_score:     int
    eta:            Optional[str]
    cargo:          Optional[str]
    recommendation: Optional[str]
    created_at:     datetime

    class Config:
        from_attributes = True


class ShipmentUpdate(BaseModel):
    status:         Optional[ShipmentStatus] = None
    risk_score:     Optional[int]            = None
    eta:            Optional[str]            = None
    recommendation: Optional[str]            = None


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id:                 str
    type:               AlertType
    severity:           Severity
    message:            str
    affected_shipments: int
    source:             str
    port:               Optional[str]
    wind_kmh:           Optional[float]
    wave_height_m:      Optional[float]
    is_active:          bool
    created_at:         datetime

    class Config:
        from_attributes = True


# ── Decisions ─────────────────────────────────────────────────────────────────

class DecisionOut(BaseModel):
    id:          int
    shipment_id: str
    action:      str
    reason:      str
    cost_impact: Optional[str]
    time_impact: Optional[str]
    confidence:  int
    was_applied: bool
    created_at:  datetime

    class Config:
        from_attributes = True


class DecisionApply(BaseModel):
    outcome: Optional[str] = None


# ── Stats ─────────────────────────────────────────────────────────────────────

class StatsOut(BaseModel):
    total_shipments:     int
    on_time:             int
    delayed:             int
    critical:            int
    avg_risk_score:      int
    disruptions_avoided: int
    savings_usd:         int
    live_alerts:         int
    high_severity:       int
