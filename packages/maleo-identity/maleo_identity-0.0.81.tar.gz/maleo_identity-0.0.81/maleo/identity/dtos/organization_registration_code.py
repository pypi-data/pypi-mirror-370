from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.identity.mixins.organization_registration_code import (
    Code,
    MaxUses,
    CurrentUses,
)


class OrganizationRegistrationCodeDTO(
    CurrentUses, MaxUses, Code, DataStatus, DataTimestamp, DataIdentifier
):
    pass
