"""
Zeeta — models.py
SQLAlchemy ORM models.
"""

import enum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ShipmentStatus(str, enum.Enum):
    on_time   = "on_time"
    delayed   = "delayed"
    critical  = "critical"
    delivered = "delivered"


class AlertType(str, enum.Enum):
    weather      = "weather"
    port         = "port"
    geopolitical = "geopolitical"
    carrier      = "carrier"


class Severity(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


class UserRole(str, enum.Enum):
    admin   = "admin"
    analyst = "analyst"
    viewer  = "viewer"


class User(Base):
    __tablename__ = "users"

    id              = Column(String,  primary_key=True)
    email           = Column(String,  unique=True, nullable=False, index=True)
    full_name       = Column(String,  nullable=False)
    hashed_password = Column(String,  nullable=False)
    role            = Column(Enum(UserRole), default=UserRole.analyst)
    company         = Column(String,  nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    last_login      = Column(DateTime(timezone=True), nullable=True)

    decisions = relationship("Decision", back_populates="user")


class Shipment(Base):
    __tablename__ = "shipments"

    id             = Column(String, primary_key=True)
    origin         = Column(String, nullable=False)
    destination    = Column(String, nullable=False)
    carrier        = Column(String, nullable=False)
    status         = Column(Enum(ShipmentStatus), default=ShipmentStatus.on_time)
    risk_score     = Column(Integer, default=0)
    eta            = Column(String,  nullable=True)
    cargo          = Column(String,  nullable=True)
    recommendation = Column(Text,    nullable=True)
    vessel_name    = Column(String,  nullable=True)
    value_usd      = Column(Float,   nullable=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    decisions = relationship("Decision", back_populates="shipment",
                             cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id                 = Column(String,  primary_key=True)
    type               = Column(Enum(AlertType), nullable=False)
    severity           = Column(Enum(Severity),  nullable=False)
    message            = Column(Text,    nullable=False)
    affected_shipments = Column(Integer, default=0)
    source             = Column(String,  default="internal")
    port               = Column(String,  nullable=True)
    region             = Column(String,  nullable=True)
    wind_kmh           = Column(Float,   nullable=True)
    wave_height_m      = Column(Float,   nullable=True)
    is_active          = Column(Boolean, default=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at        = Column(DateTime(timezone=True), nullable=True)


class Decision(Base):
    __tablename__ = "decisions"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id     = Column(String,  ForeignKey("shipments.id"), nullable=False, index=True)
    user_id         = Column(String,  ForeignKey("users.id"), nullable=True)
    action          = Column(String,  nullable=False)
    reason          = Column(Text,    nullable=False)
    cost_impact     = Column(String,  nullable=True)
    time_impact     = Column(String,  nullable=True)
    confidence      = Column(Integer, default=0)
    was_applied     = Column(Boolean, default=False)
    applied_at      = Column(DateTime(timezone=True), nullable=True)
    outcome         = Column(Text,    nullable=True)
    weather_context = Column(Text,    nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    shipment = relationship("Shipment", back_populates="decisions")
    user     = relationship("User",     back_populates="decisions")
