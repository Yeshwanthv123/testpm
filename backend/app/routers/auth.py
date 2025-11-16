from datetime import datetime, timedelta, timezone
import os
import json
import hashlib
import urllib.parse
from typing import Optional, Dict, Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..database import get_db
from ..models import User, Evaluation

router = APIRouter(tags=["auth"])

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
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    experience: Optional[str] = None
    region: Optional[str] = None
    targetCompanies: Optional[list[str]] = None

# -------------------- Email/Password Auth -------------------- #
@router.post("/register") # FIX: Changed from /signup to /register
def register(payload: SignUpIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=_sha256(payload.password),
        is_active=True,
    )
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
    if not user:
        raise HTTPException(status_code=401, detail="This email is not registered. Please sign up first.")
    
    if not user.hashed_password or user.hashed_password != _sha256(payload.password):
        raise HTTPException(status_code=401, detail="Invalid password")

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
        **({ "full_name": getattr(current, "full_name") } if hasattr(current, "full_name") else {}),
        **({ "experience": getattr(current, "experience") } if hasattr(current, "experience") else {}),
        **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
        **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
        **({ "profile_picture": getattr(current, "profile_picture") } if hasattr(current, "profile_picture") and getattr(current, "profile_picture") else {}),
    }

@router.patch("/me")
def update_me(update: UserUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
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
        **({ "region": getattr(current, "region") } if hasattr(current, "region") else {}),
        **({ "targetCompanies": getattr(current, "targetCompanies") } if hasattr(current, "targetCompanies") else {}),
    }

# -------------------- Password Management -------------------- #
class ChangePasswordPayload(BaseModel):
    currentPassword: str
    newPassword: str

@router.post("/change-password")
def change_password(
    payload: ChangePasswordPayload,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    """Change the authenticated user's password.
    
    Expects: { "currentPassword": "...", "newPassword": "..." }
    Returns: { "message": "Password updated successfully" }
    """
    # Verify current password
    if not current.hashed_password or current.hashed_password != _sha256(payload.currentPassword):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Update password
    current.hashed_password = _sha256(payload.newPassword)
    db.add(current)
    db.commit()
    
    return {"message": "Password updated successfully"}

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


# ============================================================================
# PROFILE PICTURE ENDPOINTS
# ============================================================================

@router.post("/profile-picture")
def upload_profile_picture(
    profile_picture_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload profile picture for the current user.
    Expects: { "profile_picture": "data:image/png;base64,..." }
    """
    try:
        if not profile_picture_data or "profile_picture" not in profile_picture_data:
            raise HTTPException(status_code=400, detail="No image data provided")

        image_data = profile_picture_data["profile_picture"]
        
        # Validate it's a data URL
        if not image_data.startswith("data:image/"):
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Size limit: 5MB
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image too large (max 5MB)")

        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.profile_picture = image_data
        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "Profile picture updated",
            "profile_picture": user.profile_picture
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's profile including profile picture.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "experience": current_user.experience,
        "currentRole": current_user.currentRole,
        "region": current_user.region,
        "targetCompanies": current_user.targetCompanies,
        "profile_picture": current_user.profile_picture
    }


@router.put("/profile")
def update_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user profile information.
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update allowed fields
        if "full_name" in profile_data:
            user.full_name = profile_data["full_name"]
        if "experience" in profile_data:
            user.experience = profile_data["experience"]
        if "currentRole" in profile_data:
            user.currentRole = profile_data["currentRole"]
        if "region" in profile_data:
            user.region = profile_data["region"]
        if "targetCompanies" in profile_data:
            user.targetCompanies = profile_data["targetCompanies"]

        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "Profile updated",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "experience": user.experience,
                "currentRole": user.currentRole,
                "region": user.region,
                "targetCompanies": user.targetCompanies,
                "profile_picture": user.profile_picture
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Admin / Migration -------------------- #
@router.post("/admin/migrate-regions")
def migrate_user_regions(db: Session = Depends(get_db)):
    """
    Admin endpoint to assign 'US' region to all users without one.
    This is a one-time migration to populate existing users for regional leaderboards.
    """
    try:
        # Count users without region
        users_without_region = db.query(User).filter(
            (User.region == None) | (User.region == '')
        ).all()
        
        if not users_without_region:
            return {
                "message": "All users already have regions assigned",
                "updated_count": 0
            }
        
        # Assign 'US' as default region
        for user in users_without_region:
            user.region = 'US'
        
        db.commit()
        
        return {
            "message": f"Successfully assigned 'US' region to {len(users_without_region)} users",
            "updated_count": len(users_without_region)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/create-test-users")
def create_test_users(db: Session = Depends(get_db)):
    """
    Admin endpoint to create test users with regions for leaderboard testing.
    Creates users in different regions with sample interview results.
    """
    try:
        regions = ['US', 'EU', 'Asia Pacific', 'BR', 'Africa', 'AE']
        test_users = []
        created_count = 0
        
        for region in regions:
            for i in range(1, 6):  # Create 5 test users per region
                email = f"test_{region.lower().replace(' ', '_')}_{i}@example.com"
                
                # Check if user already exists
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    continue
                
                # Create user
                user = User(
                    email=email,
                    hashed_password=_sha256("test123"),  # dummy password
                    full_name=f"Test User {region} {i}",
                    region=region,
                    experience='3-5',
                    is_active=True
                )
                db.add(user)
                db.flush()  # Get user ID
                
                # Create sample evaluation for this user
                score = 60 + (i * 5) + (hash(region) % 20)  # Varied scores
                eval_record = Evaluation(
                    user_id=user.id,
                    overall_score=score,
                    details={"per_question": []}
                )
                db.add(eval_record)
                created_count += 1
                test_users.append({"email": email, "region": region})
        
        db.commit()
        
        return {
            "message": f"Created {created_count} test users across regions",
            "test_users": test_users,
            "regions": regions
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

