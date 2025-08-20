from maleo.soma.mixins.general import OptionalOrganizationId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.metadata.schemas.data.blood_type import OptionalSimpleBloodTypeMixin
from maleo.metadata.schemas.data.gender import OptionalSimpleGenderMixin
from maleo.metadata.schemas.data.user_type import SimpleUserTypeMixin
from maleo.identity.enums.user import IdentifierType
from maleo.identity.mixins.user import (
    Username,
    Email,
    Phone,
    Password,
    PasswordConfirmation,
    RegistrationCode,
    Expand,
)
from maleo.identity.mixins.user_profile import (
    OptionalIdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    BirthPlace,
    BirthDate,
    OptionalAvatar,
    OptionalAvatarContentType,
    OptionalAvatarName,
)
from maleo.identity.types.base.user import IdentifierValueType


class ReadSingleQueryParameter(Expand, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Expand, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class ReadSinglePassword(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(Phone, Email, Username):
    pass


class UpdateParameter(
    Expand,
    UpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass


class CreateBody(Password, UpdateBody, SimpleUserTypeMixin, OptionalOrganizationId):
    pass


class CreateParameter(
    Expand,
    CreateBody,
):
    pass


class RegisterParameter(
    Expand,
    OptionalAvatarName,
    OptionalAvatarContentType,
    OptionalAvatar,
    OptionalSimpleBloodTypeMixin,
    OptionalSimpleGenderMixin,
    BirthDate,
    BirthPlace,
    EndingTitle,
    LastName,
    MiddleName,
    FirstName,
    LeadingTitle,
    OptionalIdCard,
    PasswordConfirmation,
    Password,
    Phone,
    Email,
    Username,
    RegistrationCode,
):
    pass
