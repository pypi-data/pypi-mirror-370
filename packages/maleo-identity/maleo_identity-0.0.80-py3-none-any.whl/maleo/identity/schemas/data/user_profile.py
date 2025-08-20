from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.soma.mixins.general import UserId
from maleo.metadata.schemas.data.blood_type import (
    OptionalSimpleBloodTypeMixin,
    OptionalExpandedBloodTypeMixin,
)
from maleo.metadata.schemas.data.gender import (
    OptionalSimpleGenderMixin,
    OptionalExpandedGenderMixin,
)
from maleo.identity.mixins.user_profile import (
    IdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    FullName,
    BirthPlace,
    BirthDate,
    AvatarName,
    OptionalAvatarUrl,
)


class UserProfileDataSchema(
    OptionalAvatarUrl,
    AvatarName,
    OptionalExpandedBloodTypeMixin,
    OptionalSimpleBloodTypeMixin,
    OptionalExpandedGenderMixin,
    OptionalSimpleGenderMixin,
    BirthDate,
    BirthPlace,
    FullName,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    IdCard,
    UserId,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserProfileDataMixin(BaseModel):
    profile: UserProfileDataSchema = Field(..., description="Profile.")


class OptionalUserProfileDataMixin(BaseModel):
    profile: Optional[UserProfileDataSchema] = Field(
        None, description="Profile. (Optional)"
    )
