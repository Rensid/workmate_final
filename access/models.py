from typing import Annotated
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from access.base import Base

string_field = Annotated[str, mapped_column(String(32))]
ids = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[string_field]
    hashed_password: Mapped[string_field]

    role_association: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user"
    )


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[ids]

    name: Mapped[str] = mapped_column(String(8))
    resource_type: Mapped[string_field]

    role_association: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[ids]
    name: Mapped[string_field]

    user_association: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role"
    )

    permission_association: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role"
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    id: Mapped[ids]

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"))

    role: Mapped["Role"] = relationship("Role", back_populates="permission_association")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_association"
    )


class UserRole(Base):
    __tablename__ = "user_role"

    id: Mapped[ids]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))

    role: Mapped["Role"] = relationship("Role", back_populates="user_association")
    user: Mapped["User"] = relationship("User", back_populates="role_association")
