from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer
from maleo.identity.db import MaleoIdentityBase
from maleo.soma.models.table import DataTable


class UserOrganizationsMixin:
    # Foreign Key UsersTable
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    # Foreign Key OrganizationsTable
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )


class UserOrganizationsTable(UserOrganizationsMixin, DataTable, MaleoIdentityBase):
    __tablename__ = "user_organizations"

    user = relationship(
        "UsersTable",
        back_populates="user_organization",
        cascade="all",
        lazy="select",
        uselist=False,
    )

    organization = relationship(
        "OrganizationsTable",
        back_populates="user_organization",
        cascade="all",
        lazy="select",
        uselist=False,
    )

    user_organization_roles = relationship(
        "UserOrganizationRolesTable",
        back_populates="user_organization",
        cascade="all, delete-orphan",
        lazy="select",
    )
