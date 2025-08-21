from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.metadata.enums.gender import IdentifierType
from maleo.metadata.types.base.gender import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.KEY: str,
    IdentifierType.NAME: str,
}


RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="genders", name="Genders", url_slug="genders")],
    details=None,
)
