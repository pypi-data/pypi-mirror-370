from maleo.soma.mixins.general import OptionalOrganizationId, UserId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.cds.dtos.coding.diagnosis import CompleteDiagnosisMixin
from maleo.cds.dtos.coding.procedure import CompleteProcedureMixin
from maleo.cds.dtos.coding.record import (
    PersonalRecordDTO,
    SubjectiveRecordDTO,
    ObjectiveRecordDTO,
    PlanRecordDTO,
)
from maleo.cds.enums.coding.record import IdentifierType
from maleo.cds.types.base.coding.record import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateOrUpdateBody(
    CompleteProcedureMixin,
    PlanRecordDTO,
    CompleteDiagnosisMixin,
    ObjectiveRecordDTO,
    SubjectiveRecordDTO,
    PersonalRecordDTO,
):
    pass


class CreateParameter(CreateOrUpdateBody, UserId, OptionalOrganizationId):
    pass


class UpdateParameter(
    CreateOrUpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass
