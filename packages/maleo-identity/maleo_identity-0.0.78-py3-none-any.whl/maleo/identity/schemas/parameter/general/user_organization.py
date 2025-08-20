from maleo.soma.mixins.general import OrganizationId, UserId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.identity.mixins.user_organization import Expand


class ReadSingleQueryParameter(Expand, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Expand, UseCache, OptionalListOfDataStatuses, OrganizationId, UserId
):
    pass


class CreateParameter(Expand, UserId, OrganizationId):
    pass
