from datetime import timedelta, datetime, timezone
import jwt
from passlib.context import CryptContext
from .config import settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, settings.JWT_SECRET, algorithm="HS256")
def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": subject, "exp": expire}, settings.JWT_REFRESH_SECRET, algorithm="HS256")
def decode_access(token: str) -> dict: return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
def decode_refresh(token: str) -> dict: return jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
