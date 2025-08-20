from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer
from maleo.soma.models.table import DataTable
from maleo.identity.db import MaleoIdentityBase


class UserOrganizationRolesMixin:
    # Foreign Key UserOrganizationsTable
    user_organization_id = Column(
        Integer,
        ForeignKey("user_organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    # Foreign Key OrganizationRolesTable
    organization_role_id = Column(
        Integer,
        ForeignKey("organization_roles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )


class UserOrganizationRolesTable(
    UserOrganizationRolesMixin, DataTable, MaleoIdentityBase
):
    __tablename__ = "user_organization_roles"

    user_organization = relationship(
        "UserOrganizationsTable",
        back_populates="user_organization_roles",
        cascade="all",
        lazy="select",
        uselist=False,
    )

    user = relationship(
        "UsersTable",
        secondary="user_organizations",
        primaryjoin="UserOrganizationRolesTable.user_organization_id == UserOrganizationsTable.id",
        secondaryjoin="UserOrganizationsTable.user_id == UsersTable.id",
        uselist=False,
        viewonly=True,
    )

    organization = relationship(
        "OrganizationsTable",
        secondary="user_organizations",
        primaryjoin="UserOrganizationRolesTable.user_organization_id == UserOrganizationsTable.id",
        secondaryjoin="UserOrganizationsTable.organization_id == OrganizationsTable.id",
        uselist=False,
        viewonly=True,
    )

    organization_role = relationship(
        "OrganizationRolesTable",
        back_populates="user_organization_roles",
        cascade="all",
        lazy="select",
        uselist=False,
    )
