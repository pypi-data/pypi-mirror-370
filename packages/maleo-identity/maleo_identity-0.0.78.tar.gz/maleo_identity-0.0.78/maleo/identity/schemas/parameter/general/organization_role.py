from maleo.soma.mixins.general import OrganizationId
from maleo.soma.mixins.parameter import OptionalListOfDataStatuses, UseCache
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.identity.mixins.organization_role import Key, Expand


class ReadSingleQueryParameter(Expand, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Expand, UseCache, OptionalListOfDataStatuses, Key, OrganizationId
):
    pass
