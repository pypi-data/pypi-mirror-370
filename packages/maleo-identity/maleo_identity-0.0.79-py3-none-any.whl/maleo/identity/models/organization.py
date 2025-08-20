from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Enum, UUID
from uuid import uuid4
from maleo.soma.models.table import DataTable
from maleo.metadata.enums.organization_type import OrganizationType
from maleo.identity.db import MaleoIdentityBase


class OrganizationsMixin:
    organization_type = Column(
        name="organization_type",
        type_=Enum(OrganizationType, name="organization_type"),
        default=OrganizationType.REGULAR,
        nullable=False,
    )
    parent_id = Column(
        "parent_id",
        Integer,
        ForeignKey("organizations.id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    key = Column(name="key", type_=String(255), unique=True, nullable=False)
    name = Column(name="name", type_=String(255), nullable=False)
    secret = Column(
        name="secret", type_=UUID, default=uuid4, unique=True, nullable=False
    )


class OrganizationsTable(OrganizationsMixin, DataTable, MaleoIdentityBase):
    __tablename__ = "organizations"
    parent = relationship(
        "OrganizationsTable",
        remote_side="OrganizationsTable.id",
        # back_populates="children"
    )
    # children = relationship(
    #     "OrganizationsTable",
    #     back_populates="parent",
    #     cascade="all",
    #     lazy="select",
    #     foreign_keys="[OrganizationsTable.parent_id]",
    #     order_by="OrganizationsTable.id"
    # )
    registration_code = relationship(
        "OrganizationRegistrationCodesTable",
        back_populates="organization",
        cascade="all",
        lazy="select",
        uselist=False,
    )
    user_organization = relationship(
        "UserOrganizationsTable",
        back_populates="organization",
        cascade="all, delete-orphan",
        uselist=False,
    )
    organization_roles = relationship(
        "OrganizationRolesTable",
        back_populates="organization",
        cascade="all, delete-orphan",
        uselist=False,
    )
