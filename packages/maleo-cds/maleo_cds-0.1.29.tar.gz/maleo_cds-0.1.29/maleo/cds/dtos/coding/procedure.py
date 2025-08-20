from pydantic import BaseModel, Field
from typing import List
from maleo.soma.mixins.general import Code, Description, OptionalOrganizationId, UserId
from maleo.soma.mixins.timestamp import Duration
from maleo.cds.dtos.coding.record import PlanRecordDTO
from maleo.cds.mixins.general import OptionalReasoning


class ProcedureDataDTO(
    OptionalReasoning,
    Description,
    Code[str],
):
    pass


class CompleteProcedureDTO(BaseModel):
    primary: List[ProcedureDataDTO] = Field(..., description="Primary procedures")
    alternatives: List[ProcedureDataDTO] = Field(
        ..., description="Alternative procedures"
    )


class CompleteProcedureMixin(BaseModel):
    procedure: CompleteProcedureDTO = Field(..., description="Complete procedure")


class ProcedureRecordDTO(
    Duration,
    CompleteProcedureMixin,
    PlanRecordDTO,
    UserId,
    OptionalOrganizationId,
):
    pass
