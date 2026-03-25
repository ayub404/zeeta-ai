"""
Zeeta — main.py
Entry point only. All routes live in routers/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import auth, shipments, alerts, decisions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Zeeta API",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(shipments.router, prefix="/api/shipments", tags=["shipments"])
app.include_router(alerts.router,    prefix="/api/alerts",    tags=["alerts"])
app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])


@app.get("/")
async def root():
    return {"status": "ok", "version": "3.0.0"}


@app.get("/api/stats")
async def stats():
    from services.stats import get_stats
    return await get_stats()
