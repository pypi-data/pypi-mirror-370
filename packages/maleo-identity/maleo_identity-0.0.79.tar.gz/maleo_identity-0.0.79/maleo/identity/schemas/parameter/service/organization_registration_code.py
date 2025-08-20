from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.soma.mixins.parameter import OptionalListOfOrganizationIds


class ReadMultipleFromOrganizationQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema
):
    pass


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfOrganizationIds,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema, OptionalListOfOrganizationIds
):
    pass
