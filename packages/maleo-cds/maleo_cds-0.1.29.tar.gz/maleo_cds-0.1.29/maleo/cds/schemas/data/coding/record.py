from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.soma.mixins.general import UserId, OptionalOrganizationId
from maleo.cds.dtos.coding.diagnosis import CompleteDiagnosisMixin
from maleo.cds.dtos.coding.procedure import CompleteProcedureMixin
from maleo.cds.dtos.coding.record import (
    PersonalRecordDTO,
    SubjectiveRecordDTO,
    ObjectiveRecordDTO,
    PlanRecordDTO,
)


class RecordDataSchema(
    CompleteProcedureMixin,
    PlanRecordDTO,
    CompleteDiagnosisMixin,
    ObjectiveRecordDTO,
    SubjectiveRecordDTO,
    PersonalRecordDTO,
    UserId,
    OptionalOrganizationId,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class ExpandedRecord(BaseModel):
    record: RecordDataSchema = Field(..., description="Single record data")


class OptionalExpandedRecord(BaseModel):
    record: Optional[RecordDataSchema] = Field(
        None, description="Single record data. (Optional)"
    )


class ListOfExpandedRecords(BaseModel):
    records: List[RecordDataSchema] = Field(..., description="Multiple records data")


class OptionalListOfExpandedRecords(BaseModel):
    records: Optional[List[RecordDataSchema]] = Field(
        None, description="Multiple records data. (Optional)"
    )
