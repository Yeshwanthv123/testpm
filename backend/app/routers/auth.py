from datetime import datetime, timedelta, timezone
import os
import json
import hashlib
import urllib.parse
from typing import Optional, Dict, Any

import requests  # make sure 'requests' is in backend/requirements.txt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import jwt, JWTError  # python-jose

from ..database import get_db
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

# -------------------- Config -------------------- #
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:8000").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-please")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_REDIRECT_URI = f"{OAUTH_REDIRECT_BASE}/auth/google/callback"

# -------------------- Helpers -------------------- #
def _sha256(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def _create_jwt_token(subject: Dict[str, Any], expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    claims = subject.copy()
    claims.update({"iat": int(now.timestamp()), "exp": int((now + expires_delta).timestamp())})
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int, email: str) -> str:
    return _create_jwt_token({"sub": str(user_id), "email": email, "type": "access"},
                             timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(user_id: int, email: str) -> str:
    return _create_jwt_token({"sub": str(user_id), "email": email, "type": "refresh"},
                             timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def _decode_bearer(auth_header: Optional[str]) -> Dict[str, Any]:
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    payload = _decode_bearer(authorization)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == int(user_id), User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

# -------------------- Schemas -------------------- #
class SignUpIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None  # if you store it

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    experience: Optional[str] = None
    currentRole: Optional[str] = None
    region: Optional[str] = None
    targetCompanies: Optional[list[str]] = None

# -------------------- Email/Password Auth -------------------- #
@router.post("/signup")
def signup(payload: SignUpIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=_sha256(payload.password),
        is_active=True,
    )
    # If your model has full_name column, set it via setattr guard:
    if hasattr(user, "full_name") and payload.full_name:
        setattr(user, "full_name", payload.full_name)

    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id, user.email)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email}
    }

@router.post("/login")
def login(payload: SignUpIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or user.hashed_password != _sha256(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id, user.email)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email}
    }

@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return {
        "id": current.id,
        "email": current.email,
        "is_active": current.is_active,
        "created_at": current.created_at,
        # include optional profile fields if present on your model
        **({ "full_name": getattr(current, "full_name") } if hasattr(current, "full_name") else {}),
        **({ "experience": getattr(current, "experience") } if hasattr(current, "experience") else {}),
        **({ "currentRole": getattr(current, "currentRole") } if hasattr(current, "currentRole") else {}),
        **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
        **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
    }

@router.patch("/me")
def update_me(update: UserUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    # update only known attributes on the model if they exist
    for field, value in update.dict(exclude_unset=True).items():
        if hasattr(current, field):
            setattr(current, field, value)
    db.add(current)
    db.commit()
    db.refresh(current)
    return {
        "id": current.id,
        "email": current.email,
        "is_active": current.is_active,
        "created_at": current.created_at,
        **({ "full_name": getattr(current, "full_name") } if hasattr(current, "full_name") else {}),
        **({ "experience": getattr(current, "experience") } if hasattr(current, "experience") else {}),
        **({ "currentRole": getattr(current, "currentRole") } if hasattr(current, "currentRole") else {}),
        **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
        **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
    }

# -------------------- Token Refresh -------------------- #
@router.post("/refresh")
def refresh_access_token(refresh_token: str = Query(...), db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(decoded.get("sub", "0"))
    email = decoded.get("email")
    user = db.query(User).filter(User.id == user_id, User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access = create_access_token(user.id, user.email)
    return {"access_token": new_access, "token_type": "bearer", "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}

# -------------------- Google OAuth (unchanged) -------------------- #
@router.get("/google/url")
def google_oauth_url(state: Optional[str] = Query(None), prompt_consent: bool = Query(True)):
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server.")
    scope = "openid email profile"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent" if prompt_consent else "none",
    }
    if state:
        params["state"] = state
    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return {"auth_url": url, "redirect_uri": GOOGLE_REDIRECT_URI}

@router.get("/google/callback")
def google_oauth_callback(request: Request,
                          code: Optional[str] = Query(None),
                          state: Optional[str] = Query(None),
                          redirect: bool = Query(True),
                          db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' in callback.")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured (client id/secret).")

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    try:
        token_res = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Failed to reach Google token endpoint.")
    if token_res.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_res.text}")

    token_payload = token_res.json()
    id_token = token_payload.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No id_token in Google response.")

    try:
        info_res = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token}, timeout=15)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Failed to validate id_token with Google.")
    if info_res.status_code != 200:
        raise HTTPException(status_code=401, detail="id_token validation failed.")

    claims = info_res.json()
    if claims.get("aud") != GOOGLE_CLIENT_ID or not claims.get("email") or str(claims.get("email_verified", "false")).lower() != "true":
        raise HTTPException(status_code=401, detail="Invalid Google id_token (audience/email).")

    email = claims["email"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user_id=user.id, email=user.email)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)
    payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {"id": user.id, "email": user.email},
        "state": state,
    }

    if redirect:
        fragment = urllib.parse.quote(json.dumps(payload))
        return RedirectResponse(f"{FRONTEND_URL}/#auth={fragment}", status_code=302)

    return JSONResponse(payload)
