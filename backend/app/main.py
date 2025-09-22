from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# The 'database' object is no longer used, so we remove the import
# from app.db import database 
from app.routers import auth, oauth, stubs, interview

app = FastAPI()

# CORS configuration remains the same
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The new session-based approach does not require these startup/shutdown events,
# so they have been removed.
# @app.on_event("startup")
# async def startup():
#     await database.connect()
#
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# Include all your routers
app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(stubs.router)
app.include_router(interview.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview App API"}