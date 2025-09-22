from fastapi import APIRouter, Depends, HTTPException, status, Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session
from .. import models, schemas
from ..db import get_db
from ..security import create_access_token

router = APIRouter()

# Setup OAuth
config = Config('.env')
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/me')
def get_current_user(request: Request):
    # This is a placeholder. You would typically decode a JWT here.
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# FIX: Updated route to match frontend and best practices
@router.get('/oauth/{provider}/start')
async def oauth_start(request: Request, provider: str):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # FIX: Correctly reference the new callback route name 'oauth_callback'
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await client.authorize_redirect(request, redirect_uri)

# FIX: Updated route to be clear and consistent
@router.get('/oauth/{provider}/callback', name='oauth_callback')
async def oauth_callback(request: Request, provider: str, db: Session = Depends(get_db)):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        token = await client.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Could not fetch user info")

        # Check if user exists, if not, create them
        db_user = db.query(models.User).filter(models.User.email == user_info['email']).first()
        if not db_user:
            new_user = models.User(
                email=user_info['email'],
                full_name=user_info.get('name', ''),
                # Note: Users created via OAuth won't have a password
                hashed_password="" 
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            db_user = new_user

        # Create an access token for your app
        access_token = create_access_token(data={"user_id": db_user.id})
        
        # Redirect to frontend with the token
        # In a real app, you'd want to handle this more securely
        redirect_url = f"http://localhost:3000/oauth-callback?token={access_token}"
        return { "redirect_url": redirect_url }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))