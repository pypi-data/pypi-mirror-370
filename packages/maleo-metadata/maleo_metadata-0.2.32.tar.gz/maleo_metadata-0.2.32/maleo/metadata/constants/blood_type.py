from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.metadata.enums.blood_type import IdentifierType
from maleo.metadata.types.base.blood_type import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.KEY: str,
    IdentifierType.NAME: str,
}


RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="blood_types", name="Blood Types", url_slug="blood-types"
        )
    ],
    details=None,
)
