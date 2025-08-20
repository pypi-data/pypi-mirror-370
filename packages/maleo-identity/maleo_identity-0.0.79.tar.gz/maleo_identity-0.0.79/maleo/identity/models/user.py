from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Enum
from maleo.soma.models.table import DataTable
from maleo.metadata.enums.user_type import UserType
from maleo.identity.db import MaleoIdentityBase


class UsersMixin:
    user_type = Column(
        name="user_type",
        type_=Enum(UserType, name="user_type"),
        default=UserType.REGULAR,
        nullable=False,
    )
    username = Column(name="username", type_=String(50), unique=True, nullable=False)
    email = Column(name="email", type_=String(255), unique=True, nullable=False)
    phone = Column(name="phone", type_=String(15), nullable=False)
    password = Column(name="password", type_=String(255), nullable=False)


class UsersTable(UsersMixin, DataTable, MaleoIdentityBase):
    __tablename__ = "users"

    profile = relationship(
        "UserProfilesTable",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    system_roles = relationship(
        "UserSystemRolesTable", back_populates="user", cascade="all, delete-orphan"
    )
    user_organization = relationship(
        "UserOrganizationsTable",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
