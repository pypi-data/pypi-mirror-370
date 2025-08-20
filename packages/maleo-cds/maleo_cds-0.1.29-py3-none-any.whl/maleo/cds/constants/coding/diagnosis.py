from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.cds.enums.coding.diagnosis import IdentifierType
from maleo.cds.types.base.coding.diagnosis import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(key="diagnoses", name="Diagnoses", url_slug="diagnoses")
    ],
    details=None,
)
