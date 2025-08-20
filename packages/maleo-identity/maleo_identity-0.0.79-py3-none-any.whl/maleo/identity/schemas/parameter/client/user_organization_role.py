from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.user_organization_role import Expand


class ReadMultipleFromUserOrganizationParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    UserId,
    OrganizationId,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleFromUserOrganizationQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass
