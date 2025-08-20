from maleo.soma.mixins.general import OptionalParentId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.metadata.schemas.data.organization_type import SimpleOrganizationTypeMixin
from maleo.identity.enums.organization import IdentifierType
from maleo.identity.mixins.organization import Key, Name, Expand
from maleo.identity.types.base.organization import IdentifierValueType


class ReadSingleQueryParameter(Expand, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Expand, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateOrUpdateBody(Name, Key, OptionalParentId, SimpleOrganizationTypeMixin):
    pass


class CreateParameter(
    Expand,
    CreateOrUpdateBody,
):
    pass


class UpdateParameter(
    Expand,
    CreateOrUpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass
