from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from ..db import get_db
from .. import models, schemas
from ..security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access, decode_refresh

router = APIRouter(prefix="/auth", tags=["auth"])

# Helper function to get the current user from token
def get_current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        data = decode_access(token)
        user_id = data.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.get(models.User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(models.User).where(models.User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = models.User(email=payload.email, full_name=payload.full_name or "", password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.TokenPair)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == payload.email))
    if not user or user.password_hash == "oauth" or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(str(user.id)), "refresh_token": create_refresh_token(str(user.id)), "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.TokenPair)
def refresh(payload: schemas.RefreshRequest):
    try:
        data = decode_refresh(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    uid = data.get("sub")
    return {"access_token": create_access_token(str(uid)), "refresh_token": create_refresh_token(str(uid)), "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=schemas.UserOut)
def update_me(payload: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_data = payload.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = db.scalar(select(models.User).where(models.User.email == update_data["email"]))
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already registered")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user