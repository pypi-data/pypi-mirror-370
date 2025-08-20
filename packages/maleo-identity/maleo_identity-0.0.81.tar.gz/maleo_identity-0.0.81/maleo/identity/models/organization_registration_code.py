from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, UUID
from uuid import uuid4
from maleo.soma.models.table import DataTable
from maleo.identity.db import MaleoIdentityBase


class OrganizationRegistrationCodesMixin:
    # Foreign Key OrganizationsTable
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    code = Column(name="code", type_=UUID, default=uuid4, unique=True, nullable=False)
    max_uses = Column(name="max_uses", type_=Integer, nullable=False, default=1)
    current_uses = Column(name="current_uses", type_=Integer, nullable=False, default=0)


class OrganizationRegistrationCodesTable(
    OrganizationRegistrationCodesMixin, DataTable, MaleoIdentityBase
):
    __tablename__ = "organization_registration_codes"

    organization = relationship(
        "OrganizationsTable",
        back_populates="registration_code",
        cascade="all",
        lazy="select",
        uselist=False,
    )
