from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import OptionalListOfOrganizationIds
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)


class ReadMultipleFromOrganizationParameter(
    ReadPaginatedMultipleParameterSchema, OrganizationId
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema, OptionalListOfOrganizationIds
):
    pass


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema, OptionalListOfOrganizationIds
):
    pass
