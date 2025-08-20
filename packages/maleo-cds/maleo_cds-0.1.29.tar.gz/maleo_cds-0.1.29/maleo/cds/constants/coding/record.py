from typing import Callable, Dict
from uuid import UUID
from maleo.soma.schemas.resource import Resource, ResourceIdentifier
from maleo.cds.enums.coding.record import IdentifierType
from maleo.cds.types.base.coding.record import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="records",
            name="Records",
            url_slug="records",
        )
    ],
    details=None,
)
