from pydantic import BaseModel, Field
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import UserId, OrganizationId
from .organization import OrganizationDataMixin
from .user import UserDataMixin


class UserOrganizationDataSchema(
    OrganizationDataMixin,
    OrganizationId,
    UserDataMixin,
    UserId,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationDataMixin(BaseModel):
    user_organization: UserOrganizationDataSchema = Field(
        ..., description="User organization"
    )
