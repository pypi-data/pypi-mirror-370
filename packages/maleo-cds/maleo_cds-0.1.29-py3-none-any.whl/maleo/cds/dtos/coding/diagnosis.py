from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.general import (
    Code,
    Level,
    Name,
    Description,
    OptionalOrganizationId,
    OptionalNote,
    UserId,
)
from maleo.soma.mixins.timestamp import Duration
from maleo.cds.enums.coding.diagnosis import ChosenDiagnosisLevel
from maleo.cds.mixins.general import OptionalReasoning
from maleo.cds.dtos.coding.record import (
    PersonalRecordDTO,
    SubjectiveRecordDTO,
    ObjectiveRecordDTO,
)


class DiagnosisDataDTO(
    OptionalReasoning,
    Description,
    Code[str],
):
    pass


class DiagnosisMixin(BaseModel):
    diagnosis: DiagnosisDataDTO = Field(..., description="Single diagnosis data")


class OptionalDiagnosisMixin(BaseModel):
    diagnosis: Optional[DiagnosisDataDTO] = Field(
        None, description="Single diagnosis data. (Optional)"
    )


class ListOfDiagnosesMixin(BaseModel):
    diagnoses: List[DiagnosisDataDTO] = Field(
        ..., description="Multiple diagnoses data"
    )


class OptionalListOfDiagnosesMixin(BaseModel):
    diagnoses: Optional[List[DiagnosisDataDTO]] = Field(
        None, description="Multiple diagnoses data. (Optional)"
    )


class DiagnosisRecordDTO(
    Duration,
    ListOfDiagnosesMixin,
    ObjectiveRecordDTO,
    SubjectiveRecordDTO,
    PersonalRecordDTO,
    UserId,
    OptionalOrganizationId,
):
    pass


class ChosenDiagnosisDataDTO(
    OptionalNote,
    Level[ChosenDiagnosisLevel],
    Name,
    Code[str],
):
    pass


class CompleteDiagnosisDTO(BaseModel):
    generated: List[DiagnosisDataDTO] = Field(..., description="Generated diagnoses")
    chosen: List[ChosenDiagnosisDataDTO] = Field(..., description="Chosen diagnoses")


class CompleteDiagnosisMixin(BaseModel):
    diagnosis: CompleteDiagnosisDTO = Field(..., description="Complete diagnosis")
