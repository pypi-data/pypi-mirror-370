from maleo.soma.mixins.parameter import OptionalListOfUserIds
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.metadata.schemas.data.blood_type import OptionalListOfSimpleBloodTypesMixin
from maleo.metadata.schemas.data.gender import OptionalListOfSimpleGendersMixin
from maleo.identity.mixins.user_profile import Expand


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfSimpleBloodTypesMixin,
    OptionalListOfSimpleGendersMixin,
    OptionalListOfUserIds,
):
    pass


class ReadMultipleQueryParameter(
    Expand,
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfSimpleBloodTypesMixin,
    OptionalListOfSimpleGendersMixin,
    OptionalListOfUserIds,
):
    pass
