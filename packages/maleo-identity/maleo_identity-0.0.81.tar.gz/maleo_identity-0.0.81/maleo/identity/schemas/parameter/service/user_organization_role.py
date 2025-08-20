from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
    OptionalListOfUserIds,
)
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.identity.mixins.user_organization_role import Expand


class ReadMultipleFromUserOrganizationQueryParameter(
    Expand, ReadPaginatedMultipleQueryParameterSchema, OptionalListOfKeys
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


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
):
    pass
