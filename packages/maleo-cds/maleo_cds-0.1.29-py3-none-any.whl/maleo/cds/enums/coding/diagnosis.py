from enum import StrEnum


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"


class ChosenDiagnosisLevel(StrEnum):
    PRIMARY = "primary"
    GENERAL = "general"
