from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import (
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.identity.mixins.organization_role import Expand


class ReadMultipleFromOrganizationParameter(
    Expand, ReadPaginatedMultipleParameterSchema, OptionalListOfKeys, OrganizationId
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    OptionalListOfOrganizationIds,
):
    pass


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
