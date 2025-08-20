from maleo.soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfKeys,
    OptionalListOfParentIds,
    OptionalListOfUuids,
)
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)
from maleo.metadata.schemas.data.organization_type import (
    OptionalListOfSimpleOrganizationTypesMixin,
)
from maleo.identity.mixins.organization import Expand


class ReadMultipleChildrenQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsParent,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfKeys,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfSimpleOrganizationTypesMixin,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
