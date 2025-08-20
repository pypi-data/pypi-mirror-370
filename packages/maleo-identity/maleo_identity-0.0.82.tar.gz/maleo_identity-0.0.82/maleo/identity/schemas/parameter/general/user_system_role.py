from maleo.soma.mixins.general import UserId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.metadata.schemas.data.system_role import SimpleSystemRoleMixin
from maleo.identity.mixins.user_system_role import Expand


class ReadSingleQueryParameter(
    Expand,
    ReadSingleQueryParameterSchema,
):
    pass


class ReadSingleParameter(
    Expand,
    UseCache,
    OptionalListOfDataStatuses,
    SimpleSystemRoleMixin,
    UserId,
):
    pass


class CreateParameter(
    Expand,
    SimpleSystemRoleMixin,
    UserId,
):
    pass
