
from fastapi import Depends
from access.auth.auth import get_current_user
from models import User


async def check_permissions(permission: str):
    async def checker(user: User = Depends(get_current_user)):

