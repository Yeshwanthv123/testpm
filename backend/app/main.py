from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth, oauth, stubs, interview,answer
from app.config import settings

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(oauth.router, prefix="/auth")
app.include_router(stubs.router)

# IMPORTANT: mount interview under /api so the frontend path /api/interview/questions works
app.include_router(interview.router, prefix="/api")
app.include_router(answer.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview App API"}
