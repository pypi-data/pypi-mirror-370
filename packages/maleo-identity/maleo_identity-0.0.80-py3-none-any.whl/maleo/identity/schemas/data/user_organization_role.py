from maleo.soma.mixins.data import DataIdentifier, DataTimestamp, DataStatus
from maleo.identity.schemas.data.organization_role import OrganizationRoleDataMixin
from maleo.identity.schemas.data.user_organization import UserOrganizationDataMixin


class UserOrganizationRoleDataSchema(
    OrganizationRoleDataMixin,
    UserOrganizationDataMixin,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass
