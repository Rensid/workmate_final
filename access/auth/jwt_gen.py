import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Union
from models import User
from access.router.user_schema import UserSchema
from config import settings


def verify_password(password, hashed_password) -> str:
    return settings.get_pwd().verify(password, hashed_password)


def get_password_hash(password) -> str:
    return settings.get_pwd().hash(password)


def create_token(data: dict, type: str):
    to_encode = data.copy()
    if type == "access":
        expire = datetime.now(timezone.utc) + timedelta(hours=12)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": type})
    encode_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encode_jwt


async def store_tokens(
    user_id: int,
    access_token: str,
    refresh_token: str,
    ttl_for_refresh: timedelta,
    ttl_for_access: timedelta,
):
    refresh_key = f"refresh_token:{user_id}"
    access_key = f"access_token:{user_id}"

    redis_client.setex(refresh_key, ttl_for_refresh, refresh_token)
    redis_client.setex(access_key, ttl_for_access, access_token)


def verify_refresh_token(user_id: int, refresh_token):
    key = f"refresh_token:{user_id}"
    stored_token = redis_client.get(key)
    if stored_token is None or stored_token != refresh_token:
        return False
    return True


def verify_access_token(user_id: int, access_token):
    key = f"access_token:{user_id}"
    stored_token = redis_client.get(key)
    if stored_token is None or stored_token != access_token:
        return False
    return True


async def get_new_tokens(user: User):
    user_data = UserSchema.from_orm(user)

    access_token = create_token({"sub": user_data.id}, type="access")
    refresh_token = create_token({"sub": user_data.id}, type="refresh")
    await store_tokens(
        user_data.id,
        access_token,
        refresh_token,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
    )

    return {"access": access_token, "refresh": refresh_token}
