from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import engine, Base
from .routers import auth as auth_router
from .routers import stubs as stubs_router
from .routers import oauth as oauth_router
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.APP_NAME)
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins else ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.include_router(auth_router.router)
app.include_router(stubs_router.router)
app.include_router(oauth_router.router)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
