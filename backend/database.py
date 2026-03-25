"""
Zeeta — database.py
Async PostgreSQL connection via SQLAlchemy + asyncpg.
"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://zeeta_user:zeeta_pass@localhost:5432/zeeta_db"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_demo_data()
    print("[Zeeta] Database ready.")


async def ping_db() -> bool:
    try:
        async with AsyncSessionLocal() as s:
            await s.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def _seed_demo_data():
    from sqlalchemy import select, func
    from models import Shipment, ShipmentStatus

    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count()).select_from(Shipment))
        if count and count > 0:
            return

        demo = [
            Shipment(id="ZT-001", origin="Shanghai",    destination="Rotterdam",
                     carrier="COSCO",           status=ShipmentStatus.critical,
                     risk_score=87, eta="Dec 18", cargo="Electronics",
                     recommendation="Reroute via Suez — saves 4 days vs Cape Horn"),
            Shipment(id="ZT-002", origin="Los Angeles", destination="Hamburg",
                     carrier="Maersk",          status=ShipmentStatus.delayed,
                     risk_score=64, eta="Dec 22", cargo="Auto Parts",
                     recommendation="Switch 30% of cargo to air freight"),
            Shipment(id="ZT-003", origin="Singapore",  destination="New York",
                     carrier="MSC",             status=ShipmentStatus.on_time,
                     risk_score=21, eta="Dec 20", cargo="Textiles"),
            Shipment(id="ZT-004", origin="Dubai",       destination="Mumbai",
                     carrier="Emirates SkyCargo", status=ShipmentStatus.on_time,
                     risk_score=15, eta="Dec 16", cargo="Pharmaceuticals"),
            Shipment(id="ZT-005", origin="Busan",       destination="Long Beach",
                     carrier="HMM",             status=ShipmentStatus.delayed,
                     risk_score=55, eta="Dec 25", cargo="Consumer Goods",
                     recommendation="Split shipment — 60% air, 40% next vessel"),
            Shipment(id="ZT-006", origin="Felixstowe", destination="Toronto",
                     carrier="Hapag-Lloyd",     status=ShipmentStatus.delivered,
                     risk_score=0,  eta="Dec 10", cargo="Machinery"),
        ]
        db.add_all(demo)
        await db.commit()
        print("[Zeeta] Demo shipments seeded.")
