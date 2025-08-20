from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import OptionalParentId
from maleo.metadata.schemas.data.organization_type import (
    SimpleOrganizationTypeMixin,
    OptionalExpandedOrganizationTypeMixin,
)
from maleo.identity.mixins.organization import Key, Name
from .organization_registration_code import (
    OptionalOrganizationRegistrationCodeDataMixin,
)


class OrganizationDataSchema(
    OptionalOrganizationRegistrationCodeDataMixin,
    Name,
    Key,
    OptionalParentId,
    OptionalExpandedOrganizationTypeMixin,
    SimpleOrganizationTypeMixin,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class OrganizationDataMixin(BaseModel):
    organization: OrganizationDataSchema = Field(..., description="Organization.")


class OptionalOrganizationDataMixin(BaseModel):
    organization: Optional[OrganizationDataSchema] = Field(
        None, description="Organization. (Optional)"
    )
