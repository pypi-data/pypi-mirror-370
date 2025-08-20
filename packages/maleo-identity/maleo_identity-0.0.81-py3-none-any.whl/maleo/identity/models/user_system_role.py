from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, Integer
from maleo.soma.models.table import DataTable
from maleo.metadata.enums.system_role import SystemRole
from maleo.identity.db import MaleoIdentityBase


class UserSystemRolesMixin:
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    system_role = Column(
        name="system_role",
        type_=Enum(SystemRole, name="system_role"),
        default=SystemRole.USER,
        nullable=False,
    )


class UserSystemRolesTable(UserSystemRolesMixin, DataTable, MaleoIdentityBase):
    __tablename__ = "user_system_roles"
    # Foreign Key and Relationship to UsersTable
    user = relationship("UsersTable", back_populates="system_roles")
