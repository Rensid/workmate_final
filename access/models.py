from typing import Annotated
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import Base


string_field = Annotated[str, mapped_column(String(32))]
ids = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[ids]

    name: Mapped[string_field]
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

    resource_association: Mapped[list["ResourcePermissions"]] = relationship(
        "ResourcePermissions", back_populates="permission"
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


class Resource(Base):
    __tablename__ = "resource"

    id: Mapped[ids]
    name: Mapped[string_field]

    permission_association: Mapped[list["ResourcePermissions"]] = relationship(
        "ResourcePermissions", back_populates="resource"
    )


class ResourcePermissions(Base):
    __tablename__ = "resource_permissions"

    id: Mapped[ids]

    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"))

    resource: Mapped["Resource"] = relationship(
        "Resource", back_populates="permission_association"
    )
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="resource_association"
    )
