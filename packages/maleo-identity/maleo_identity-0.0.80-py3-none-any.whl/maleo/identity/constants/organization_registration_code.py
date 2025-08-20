from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.organization_registration_code import IdentifierType
from maleo.identity.types.base.organization_registration_code import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.ORGANIZATION_ID: int,
    IdentifierType.CODE: UUID,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_registration_codes",
            name="Organization Registration Codes",
            url_slug="organization-registration-codes",
        )
    ],
    details=None,
)
