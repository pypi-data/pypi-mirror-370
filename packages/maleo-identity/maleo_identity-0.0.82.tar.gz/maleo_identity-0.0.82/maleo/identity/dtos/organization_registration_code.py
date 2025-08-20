from maleo.soma.mixins.general import OrganizationId
from maleo.identity.mixins.organization_registration_code import (
    Code,
    MaxUses,
    CurrentUses,
)


class OrganizationRegistrationCodeDTO(
    CurrentUses,
    MaxUses,
    Code,
    OrganizationId,
):
    pass
