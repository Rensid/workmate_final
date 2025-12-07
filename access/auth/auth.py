from fastapi import Depends, HTTPException, status
from app.auth.jwt import get_new_tokens, verify_access_token, verify_password, verify_refresh_token
from app.crud.user_crud import check_user_by_id, check_user_by_username
from app.base.base import main_db
from app.schemas.user_schema import TokenData
from settings import oauth2_scheme
from sqlalchemy.ext.asyncio import AsyncSession
from config import SECRET_KEY

import jwt
from jwt.exceptions import InvalidTokenError


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await check_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(session: AsyncSession = Depends(main_db.get_async_session),
                           token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # дешифровка токена и получение его типа и зашифрованного id
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id: str = payload.get("sub")
        type: str = payload.get('type')
        if user_id is None or type is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
        # проверка существования пользователя с таким id
        user = await check_user_by_id(session, id=token_data.id)
        if user is None:
            raise credentials_exception
        if type == "access":
            # проверяем, что в redis сохранен такой токен
            if not verify_access_token(token_data.id, token):
                raise credentials_exception
            return user
        elif type == "refresh":
            # проверяем, что в redis сохранен такой токен
            if not verify_refresh_token(token_data.id, token):
                raise credentials_exception
            # если такой токен есть, то возвращаем новую пару токенов
            tokens = await get_new_tokens(user)
            return {"user": user, "token": tokens}
        else:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
