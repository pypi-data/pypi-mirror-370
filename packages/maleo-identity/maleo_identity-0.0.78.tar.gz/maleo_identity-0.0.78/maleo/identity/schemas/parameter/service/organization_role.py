from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
)
from maleo.identity.mixins.organization_role import Expand


class ReadMultipleFromOrganizationQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
):
    pass
