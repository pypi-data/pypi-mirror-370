from maleo.soma.mixins.parameter import OptionalListOfUserIds
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.metadata.schemas.data.system_role import OptionalSimpleSystemRoleMixin
from maleo.identity.mixins.user_system_role import Expand


class ReadMultipleFromuserQueryParameter(
    Expand, ReadPaginatedMultipleQueryParameterSchema, OptionalSimpleSystemRoleMixin
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalSimpleSystemRoleMixin,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalSimpleSystemRoleMixin,
    OptionalListOfUserIds,
):
    pass
