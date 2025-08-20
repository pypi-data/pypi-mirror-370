from typing import Dict, List
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.organization import (
    ExpandableField as OrganizationExpandableField,
)
from maleo.identity.enums.organization_role import (
    ExpandableField as OrganizationRoleExpandableField,
)

EXPANDABLE_FIELDS_DEPENDENCIES_MAP: Dict[
    OrganizationRoleExpandableField, List[OrganizationRoleExpandableField]
] = {
    OrganizationRoleExpandableField.ORGANIZATION: [
        OrganizationRoleExpandableField.ORGANIZATION_TYPE,
        OrganizationRoleExpandableField.REGISTRATION_CODE,
    ]
}

ORGANIZATION_EXPANDABLE_FIELDS_MAP: Dict[
    OrganizationRoleExpandableField, OrganizationExpandableField
] = {
    OrganizationRoleExpandableField.ORGANIZATION_TYPE: OrganizationExpandableField.ORGANIZATION_TYPE,
    OrganizationRoleExpandableField.REGISTRATION_CODE: OrganizationExpandableField.REGISTRATION_CODE,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_roles",
            name="Organization Roles",
            url_slug="organization-roles",
        )
    ],
    details=None,
)
