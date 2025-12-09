from fastapi import Depends, HTTPException, status
from users.auth.jwt_gen import (
    get_new_tokens,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from access.views import get_user_by_id
from base import get_async_session
from access.schemas import TokenData
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

import jwt
from jwt.exceptions import InvalidTokenError


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await check_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(settings.get_oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # дешифровка токена и получение его типа и зашифрованного id
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        type: str = payload.get("type")
        jti: str = payload.get("jti")
        if user_id is None or type is None:
            raise credentials_exception
        # проверка существования пользователя с таким id
        user = await get_user_by_id(session, id=user_id)
        if user is None:
            raise credentials_exception
        if type == "access":
            # проверяем, что в redis сохранен такой токен
            if not verify_access_token(jti, token):
                raise credentials_exception
            return user
        elif type == "refresh":
            # проверяем, что в redis сохранен такой токен
            if not verify_refresh_token(jti, token):
                raise credentials_exception
            # если такой токен есть, то возвращаем новую пару токенов
            tokens = await get_new_tokens(user)
            return {"user": user, "token": tokens}
        else:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
