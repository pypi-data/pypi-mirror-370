from typing import Callable, Dict
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.identity.enums.user_profile import IdentifierType, ValidImageMimeType
from maleo.identity.types.base.user_profile import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.USER_ID: int,
    IdentifierType.ID_CARD: str,
}

MIME_TYPE_EXTENSION_MAP: Dict[ValidImageMimeType, str] = {
    ValidImageMimeType.JPEG: ".jpeg",
    ValidImageMimeType.JPG: ".jpg",
    ValidImageMimeType.PNG: ".png",
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_profiles", name="User Profiles", url_slug="user-profiles"
        )
    ],
    details=None,
)
