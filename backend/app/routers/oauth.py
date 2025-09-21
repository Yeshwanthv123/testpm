from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..config import settings
from ..db import get_db
from .. import models
from ..security import create_access_token, create_refresh_token
router = APIRouter(prefix="/auth/oauth", tags=["oauth"])
star_cfg = StarletteConfig(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID or "",
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET or "",
    "LINKEDIN_CLIENT_ID": settings.LINKEDIN_CLIENT_ID or "",
    "LINKEDIN_CLIENT_SECRET": settings.LINKEDIN_CLIENT_SECRET or "",
})
oauth = OAuth(star_cfg)
oauth.register(name="google", client_id=settings.GOOGLE_CLIENT_ID or "", client_secret=settings.GOOGLE_CLIENT_SECRET or "", server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", client_kwargs={"scope": "openid email profile"})
oauth.register(name="linkedin", client_id=settings.LINKEDIN_CLIENT_ID or "", client_secret=settings.LINKEDIN_CLIENT_SECRET or "", access_token_url="https://www.linkedin.com/oauth/v2/accessToken", authorize_url="https://www.linkedin.com/oauth/v2/authorization", api_base_url="https://api.linkedin.com/v2/", client_kwargs={"scope": "r_liteprofile r_emailaddress"})
def _redir(access: str, refresh: str) -> RedirectResponse:
    return RedirectResponse(f"{settings.FRONTEND_URL}/oauth/callback?access_token={access}&refresh_token={refresh}")
@router.get("/{provider}/start")
async def start(provider: str, request: Request):
    if provider not in ("google", "linkedin"): raise HTTPException(404, "Unknown provider")
    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/auth/oauth/{provider}/callback"
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)
@router.get("/{provider}/callback")
async def callback(provider: str, request: Request, db: Session = Depends(get_db)):
    if provider not in ("google", "linkedin"): raise HTTPException(404, "Unknown provider")
    client = oauth.create_client(provider); token = await client.authorize_access_token(request)
    if provider == "google":
        userinfo = await client.parse_id_token(request, token); email = userinfo.get("email"); full_name = userinfo.get("name")
    else:
        prof = (await client.get("me", token=token)).json()
        full_name = f"{prof.get('localizedFirstName','')} {prof.get('localizedLastName','')}".strip()
        elems = (await client.get("emailAddress?q=members&projection=(elements*(handle~))", token=token)).json().get("elements", [])
        email = (elems[0].get("handle~", {}).get("emailAddress") if elems else None)
    if not email: raise HTTPException(400, "Could not retrieve email from provider")
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if not existing:
        user = models.User(email=email, full_name=full_name or "", password_hash="oauth"); db.add(user); db.commit(); db.refresh(user)
    else: user = existing
    access = create_access_token(str(user.id)); refresh = create_refresh_token(str(user.id))
    return _redir(access, refresh)
