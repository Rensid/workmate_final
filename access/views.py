from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User


async def get_user_by_id(id: int, session: AsyncSession):
    user = session.execute(select(User).where(User.id == id))
