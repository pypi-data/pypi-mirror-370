from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.organization import IdentifierType
from maleo.identity.types.base.organization import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {IdentifierType.ID: int, IdentifierType.UUID: UUID, IdentifierType.KEY: str}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organizations", name="Organizations", url_slug="organizations"
        )
    ],
    details=None,
)
