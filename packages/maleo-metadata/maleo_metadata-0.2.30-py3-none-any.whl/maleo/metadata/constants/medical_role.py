from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.types.base.medical_role import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.CODE: str,
    IdentifierType.KEY: str,
    IdentifierType.NAME: str,
}


RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="medical_roles", name="Medical Roles", url_slug="medical-roles"
        )
    ],
    details=None,
)
