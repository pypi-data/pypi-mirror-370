from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import IdentifierTypeValue as IdentifierTypeValueMixin
from maleo.soma.schemas.parameter.general import (
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.identity.enums.organization_registration_code import IdentifierType
from maleo.identity.mixins.organization_registration_code import (
    MaxUses,
    OptionalMaxUses,
)
from maleo.identity.types.base.organization_registration_code import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateParameter(
    MaxUses,
    OrganizationId,
):
    pass


class FullUpdateBody(MaxUses):
    pass


class FullUpdateParameter(
    FullUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class PartialUpdateBody(OptionalMaxUses):
    pass


class PartialUpdateParameter(
    PartialUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateQueryParameterSchema,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
