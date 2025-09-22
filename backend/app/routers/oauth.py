from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
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

# GOOGLE — OIDC
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID or "",
    client_secret=settings.GOOGLE_CLIENT_SECRET or "",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    api_base_url="https://openidconnect.googleapis.com/v1/",   # ← add base so client.get("userinfo") has a full URL
    client_kwargs={"scope": "openid email profile"},
)

# LINKEDIN — OAuth2
oauth.register(
    name="linkedin",
    client_id=settings.LINKEDIN_CLIENT_ID or "",
    client_secret=settings.LINKEDIN_CLIENT_SECRET or "",
    access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
    authorize_url="https://www.linkedin.com/oauth/v2/authorization",
    api_base_url="https://api.linkedin.com/v2/",
    client_kwargs={"scope": "r_liteprofile r_emailaddress"},
)

def _success_redirect(access: str, refresh: str) -> RedirectResponse:
    return RedirectResponse(
        f"{settings.FRONTEND_URL}/oauth/callback?access_token={access}&refresh_token={refresh}"
    )

@router.get("/{provider}/start")
async def oauth_start(provider: str, request: Request):
    if provider not in ("google", "linkedin"):
        raise HTTPException(404, "Unknown provider")
    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/auth/oauth/{provider}/callback"
    client = oauth.create_client(provider)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    if provider not in ("google", "linkedin"):
        raise HTTPException(404, "Unknown provider")

    client = oauth.create_client(provider)

    # do NOT pass redirect_uri again; Authlib kept it in session
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as e:
        body = None
        try:
            body = e.response.json()
        except Exception:
            try:
                body = {"raw": e.response.text}
            except Exception:
                body = None
        return JSONResponse(
            status_code=400,
            content={"detail": f"OAuth error: {e.error} - {e.description}", "provider_response": body},
        )

    email = None
    full_name = None

    if provider == "google":
        # Prefer ID token; fall back to userinfo if not present
        try:
            userinfo = await client.parse_id_token(request, token)
            email = userinfo.get("email")
            full_name = userinfo.get("name")
        except Exception:
            # relative path now works because api_base_url is set
            try:
                resp = await client.get("userinfo", token=token)
            except Exception:
                # absolute fallback in case metadata changes
                resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
            data = resp.json()
            email = data.get("email")
            full_name = data.get("name") or f"{data.get('given_name','')} {data.get('family_name','')}".strip()
    else:
        prof = (await client.get("me", token=token)).json()
        full_name = f"{prof.get('localizedFirstName','')} {prof.get('localizedLastName','')}".strip()
        elems = (await client.get("emailAddress?q=members&projection=(elements*(handle~))", token=token)).json().get("elements", [])
        email = (elems[0].get("handle~", {}).get("emailAddress") if elems else None)

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from provider")

    existing = db.scalar(select(models.User).where(models.User.email == email))
    if not existing:
        user = models.User(email=email, full_name=full_name or "", password_hash="oauth")
        db.add(user); db.commit(); db.refresh(user)
    else:
        user = existing

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return _success_redirect(access, refresh)
