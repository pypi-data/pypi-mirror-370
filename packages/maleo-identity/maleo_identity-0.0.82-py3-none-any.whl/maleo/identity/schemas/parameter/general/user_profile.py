from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import IdentifierTypeValue as IdentifierTypeValueMixin
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.metadata.schemas.data.blood_type import OptionalSimpleBloodTypeMixin
from maleo.metadata.schemas.data.gender import OptionalSimpleGenderMixin
from maleo.identity.enums.user_profile import IdentifierType
from maleo.identity.mixins.user_profile import (
    Expand,
    OptionalIdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    BirthPlace,
    BirthDate,
    OptionalAvatarName,
    AvatarData,
)
from maleo.identity.types.base.user_profile import IdentifierValueType


class ReadSingleQueryParameter(
    Expand,
    ReadSingleQueryParameterSchema,
):
    pass


class ReadSingleParameter(
    Expand, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateOrUpdateQuery(Expand):
    pass


class CreateOrUpdateBody(
    OptionalAvatarName,
    OptionalSimpleGenderMixin,
    OptionalSimpleBloodTypeMixin,
    BirthDate,
    BirthPlace,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    OptionalIdCard,
    UserId,
):
    pass


class CreateParameter(AvatarData, CreateOrUpdateBody, CreateOrUpdateQuery):
    pass


class UpdateParameter(
    AvatarData,
    CreateOrUpdateBody,
    CreateOrUpdateQuery,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
