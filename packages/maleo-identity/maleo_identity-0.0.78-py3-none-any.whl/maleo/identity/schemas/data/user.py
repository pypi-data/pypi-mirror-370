from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.metadata.schemas.data.user_type import (
    SimpleUserTypeMixin,
    OptionalExpandedUserTypeMixin,
)
from maleo.identity.mixins.user import Username, Email, Phone
from .user_profile import OptionalUserProfileDataMixin
from .user_system_role import ListOfUserSystemRolesDataMixin


class UserDataSchema(
    OptionalUserProfileDataMixin,
    ListOfUserSystemRolesDataMixin,
    Phone,
    Email,
    Username,
    OptionalExpandedUserTypeMixin,
    SimpleUserTypeMixin,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserDataMixin(BaseModel):
    user: UserDataSchema = Field(..., description="User.")


class OptionalUserDataMixin(BaseModel):
    user: Optional[UserDataSchema] = Field(None, description="User. (Optional)")
