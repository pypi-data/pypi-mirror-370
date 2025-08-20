from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import (
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.user_organization import Expand


class ReadMultipleFromUserParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfOrganizationIds,
    UserId,
):
    pass


class ReadMultipleFromOrganizationParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfUserIds,
    OrganizationId,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromUserQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromOrganizationQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass
