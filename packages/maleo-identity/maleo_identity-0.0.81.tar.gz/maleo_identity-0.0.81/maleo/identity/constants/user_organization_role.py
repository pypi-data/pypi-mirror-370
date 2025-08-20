from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user import ExpandableField as UserExpandableField
from maleo.identity.enums.organization import (
    ExpandableField as OrganizationExpandableField,
)
from maleo.identity.enums.user_organization_role import (
    ExpandableField as UserOrganizationRoleExpandableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    UserOrganizationRoleExpandableField, List[UserOrganizationRoleExpandableField]
] = {
    UserOrganizationRoleExpandableField.USER: [
        UserOrganizationRoleExpandableField.USER_TYPE,
        UserOrganizationRoleExpandableField.PROFILE,
    ],
    UserOrganizationRoleExpandableField.ORGANIZATION: [
        UserOrganizationRoleExpandableField.ORGANIZATION_TYPE,
        UserOrganizationRoleExpandableField.REGISTRATION_CODE,
    ],
}

USER_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationRoleExpandableField, UserExpandableField
] = {
    UserOrganizationRoleExpandableField.USER_TYPE: UserExpandableField.USER_TYPE,
    UserOrganizationRoleExpandableField.PROFILE: UserExpandableField.PROFILE,
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationRoleExpandableField, OrganizationExpandableField
] = {
    UserOrganizationRoleExpandableField.ORGANIZATION_TYPE: OrganizationExpandableField.ORGANIZATION_TYPE,
    UserOrganizationRoleExpandableField.REGISTRATION_CODE: OrganizationExpandableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_organization_roles",
            name="UserOrganization Roles",
            url_slug="user-organization-roles",
        )
    ],
    details=None,
)
