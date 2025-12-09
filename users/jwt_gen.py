import jwt
from datetime import datetime, timedelta, timezone
from models import User
from access.router.user_schema import UserSchema
from config import settings
import secrets

redis_client = settings.get_redis_client()

def verify_password(password: str, hashed_password: str) -> bool:
    return settings.get_pwd().verify(password, hashed_password)


def get_password_hash(password: str) -> str:
    return settings.get_pwd().hash(password)



def create_token(data: dict, type: str):
    now = datetime.now(timezone.utc)
    jti = secrets.token_hex(16)  

    payload = data.copy()
    payload["iat"] = now
    payload["jti"] = jti
    payload["type"] = type

    if type == "access":
        expire = now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload["exp"] = expire

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token, jti

async def store_tokens(
        access_token: str,
        refresh_token: str,
        access_jti: str,
        refresh_jti: str,
        access_ttl: timedelta,
        refresh_ttl: timedelta,
):
    redis_client.setex(f"access_token:{access_jti}", access_ttl, access_token)
    redis_client.setex(f"refresh_token:{refresh_jti}", refresh_ttl, refresh_token)


def verify_access_token(jti: str, token: str) -> bool:
    stored = redis_client.get(f"access_token:{jti}")
    return stored is not None and stored == token


def verify_refresh_token(jti: str, token: str) -> bool:
    stored = redis_client.get(f"refresh_token:{jti}")
    return stored is not None and stored == token


async def get_new_tokens(user: User):
    user_data = UserSchema.from_orm(user)
    access_token, access_jti = create_token({"sub": user_data.id}, "access")
    refresh_token, refresh_jti = create_token({"sub": user_data.id}, "refresh")

    await store_tokens(
        access_token=access_token,
        refresh_token=refresh_token,
        access_jti=access_jti,
        refresh_jti=refresh_jti,
        access_ttl=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        refresh_ttl=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return {"access": access_token, "refresh": refresh_token}
