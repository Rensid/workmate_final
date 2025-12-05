from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from access.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
