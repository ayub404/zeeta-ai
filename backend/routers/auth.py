"""
Zeeta — routers/auth.py
Register, login, me endpoints.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from database import get_db
from models import User
from schemas import RegisterRequest, TokenResponse, UserOut
from auth_utils import hash_password, verify_password, create_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        company=body.company,
    )
    db.add(user)
    await db.commit()

    token = create_token(user.id, user.email, user.role.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form.username.lower()))
    user   = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_token(user.id, user.email, user.role.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
