from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.identity.enums.organization_registration_code import IdentifierType
from maleo.identity.mixins.organization_registration_code import MaxUses
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


class UpdateParameter(
    MaxUses,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass
