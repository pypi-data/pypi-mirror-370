from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.mixins.parameter import Expand as BaseExpand
from maleo.soma.types.base import OptionalDate, OptionalString
from maleo.identity.enums.user_profile import ExpandableField


class Expand(BaseExpand[ExpandableField]):
    pass


class IdCard(BaseModel):
    id_card: str = Field(..., max_length=16, description="User's ID Card")


class OptionalIdCard(BaseModel):
    id_card: OptionalString = Field(
        None, max_length=16, description="Optional User's ID Card"
    )


class LeadingTitle(BaseModel):
    leading_title: OptionalString = Field(
        None, max_length=25, description="User's leading title"
    )


class FirstName(BaseModel):
    first_name: str = Field(..., max_length=50, description="User's first name")


class MiddleName(BaseModel):
    middle_name: OptionalString = Field(
        None, max_length=50, description="User's middle name"
    )


class LastName(BaseModel):
    last_name: str = Field(..., max_length=50, description="User's last name")


class EndingTitle(BaseModel):
    ending_title: OptionalString = Field(
        None, max_length=25, description="User's ending title"
    )


class FullName(BaseModel):
    full_name: str = Field(..., max_length=200, description="User's full name")


class BirthPlace(BaseModel):
    birth_place: OptionalString = Field(
        None, max_length=50, description="User's birth place"
    )


class BirthDate(BaseModel):
    birth_date: OptionalDate = Field(None, description="User's birth date")


class AvatarName(BaseModel):
    avatar_name: str = Field(..., description="User's avatar's name")


class OptionalAvatarUrl(BaseModel):
    avatar_url: OptionalString = Field(None, description="Avatar's URL")


class OptionalAvatar(BaseModel):
    avatar: Optional[bytes] = Field(None, description="Optional Avatar")


class OptionalAvatarName(BaseModel):
    avatar_name: OptionalString = Field(None, description="Optional avatar's name")


class OptionalAvatarContentType(BaseModel):
    content_type: OptionalString = Field(
        None, description="Optional avatar's content type"
    )


class AvatarData(
    OptionalAvatarContentType,
    OptionalAvatar,
):
    pass
