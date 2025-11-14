from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
import os
import json
import urllib.parse
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..routers.auth import create_access_token, create_refresh_token
import requests

router = APIRouter(prefix="/oauth", tags=["oauth"])

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:8000").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_CALLBACK_URI = f"{OAUTH_REDIRECT_BASE}/oauth/google/callback"

@router.get('/google/start')
def google_oauth_start(request: Request):
    """Initiate Google OAuth flow"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured (missing CLIENT_ID)")
    
    # Build the authorization URL
    auth_params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_CALLBACK_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    
    return RedirectResponse(url=auth_url)

@router.get('/google/callback')
def google_oauth_callback(code: str = None, state: str = None, error: str = None, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Exchange authorization code for tokens
    try:
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_CALLBACK_URI,
            'grant_type': 'authorization_code',
        }
        
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data, timeout=10)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        id_token = token_json.get('id_token')
        if not id_token:
            raise HTTPException(status_code=400, detail="No id_token in response")
        
        # Get user info
        user_info_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={'Authorization': f'Bearer {token_json.get("access_token")}'},
            timeout=10
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
        
        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Could not get email from Google")
        
        # Find or create user
        db_user = db.query(models.User).filter(models.User.email == email).first()
        if not db_user:
            db_user = models.User(
                email=email,
                full_name=user_info.get('name', ''),
                is_active=True,
                hashed_password=None  # OAuth users have no password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
        # Create tokens
        access_token = create_access_token(db_user.id, db_user.email)
        refresh_token = create_refresh_token(db_user.id, db_user.email)
        
        # Redirect to frontend with tokens in hash (safe from logging)
        redirect_params = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
        }
        redirect_url = f"{FRONTEND_URL}/#auth={urllib.parse.quote(json.dumps(redirect_params))}"
        
        return RedirectResponse(url=redirect_url)
        
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to get Google tokens: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {str(e)}")

@router.get('/me')
def get_current_user_oauth(request: Request):
    """Get current OAuth user from session (placeholder)"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
