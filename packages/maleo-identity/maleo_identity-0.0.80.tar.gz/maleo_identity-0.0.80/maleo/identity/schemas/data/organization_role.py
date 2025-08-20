from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import IsDefault, Order, OrganizationId
from maleo.identity.mixins.organization_role import Key, Name
from .organization import OptionalOrganizationDataMixin


class OrganizationRoleDataSchema(
    Name,
    Key,
    Order,
    IsDefault,
    OptionalOrganizationDataMixin,
    OrganizationId,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class OrganizationRoleDataMixin(BaseModel):
    organization_role: OrganizationRoleDataSchema = Field(
        ..., description="Organization role."
    )


class OptionalOrganizationRoleDataMixin(BaseModel):
    organization_role: Optional[OrganizationRoleDataSchema] = Field(
        None, description="Organization role. (Optional)"
    )
