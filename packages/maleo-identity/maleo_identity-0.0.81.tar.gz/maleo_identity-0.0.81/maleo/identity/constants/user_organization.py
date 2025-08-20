from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user import ExpandableField as UserExpandableField
from maleo.identity.enums.organization import (
    ExpandableField as OrganizationExpandableField,
)
from maleo.identity.enums.user_organization import (
    ExpandableField as UserOrganizationExpandableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    UserOrganizationExpandableField, List[UserOrganizationExpandableField]
] = {
    UserOrganizationExpandableField.USER: [
        UserOrganizationExpandableField.USER_TYPE,
        UserOrganizationExpandableField.PROFILE,
    ],
    UserOrganizationExpandableField.PROFILE: [
        UserOrganizationExpandableField.BLOOD_TYPE,
        UserOrganizationExpandableField.GENDER,
    ],
    UserOrganizationExpandableField.SYSTEM_ROLES: [
        UserOrganizationExpandableField.SYSTEM_ROLE_DETAILS
    ],
    UserOrganizationExpandableField.ORGANIZATION: [
        UserOrganizationExpandableField.ORGANIZATION_TYPE,
        UserOrganizationExpandableField.REGISTRATION_CODE,
    ],
}

USER_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationExpandableField, UserExpandableField
] = {
    UserOrganizationExpandableField.USER_TYPE: UserExpandableField.USER_TYPE,
    UserOrganizationExpandableField.PROFILE: UserExpandableField.PROFILE,
    UserOrganizationExpandableField.BLOOD_TYPE: UserExpandableField.BLOOD_TYPE,
    UserOrganizationExpandableField.GENDER: UserExpandableField.GENDER,
    UserOrganizationExpandableField.SYSTEM_ROLES: UserExpandableField.SYSTEM_ROLES,
    UserOrganizationExpandableField.SYSTEM_ROLE_DETAILS: UserExpandableField.SYSTEM_ROLE_DETAILS,
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    UserOrganizationExpandableField, OrganizationExpandableField
] = {
    UserOrganizationExpandableField.ORGANIZATION_TYPE: OrganizationExpandableField.ORGANIZATION_TYPE,
    UserOrganizationExpandableField.REGISTRATION_CODE: OrganizationExpandableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_organizations",
            name="User Organizations",
            url_slug="user-organizations",
        )
    ],
    details=None,
)
