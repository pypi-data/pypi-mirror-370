from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import OptionalListOfUserIds
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.metadata.schemas.data.system_role import OptionalListOfSimpleSystemRolesMixin
from maleo.identity.mixins.user_system_role import Expand


class ReadMultipleFromUserParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    UserId,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleFromUserQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleSystemRolesMixin,
    OptionalListOfUserIds,
):
    pass
