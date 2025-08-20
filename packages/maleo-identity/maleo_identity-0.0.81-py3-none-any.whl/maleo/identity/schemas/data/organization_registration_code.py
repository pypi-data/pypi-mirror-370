from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import OrganizationId
from maleo.identity.mixins.organization_registration_code import (
    Code,
    MaxUses,
    CurrentUses,
)


class OrganizationRegistrationCodeDataSchema(
    CurrentUses,
    MaxUses,
    Code,
    OrganizationId,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class OrganizationRegistrationCodeDataMixin(BaseModel):
    registration_code: OrganizationRegistrationCodeDataSchema = Field(
        ..., description="Organization's Registration Code."
    )


class OptionalOrganizationRegistrationCodeDataMixin(BaseModel):
    registration_code: Optional[OrganizationRegistrationCodeDataSchema] = Field(
        None, description="Organization's Registration Code. (Optional)"
    )
