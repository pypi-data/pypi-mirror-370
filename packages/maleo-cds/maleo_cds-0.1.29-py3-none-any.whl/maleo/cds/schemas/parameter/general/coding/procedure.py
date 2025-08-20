from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.cds.dtos.coding.record import PlanRecordDTO
from maleo.cds.enums.coding.procedure import IdentifierType
from maleo.cds.types.base.coding.procedure import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class GenerateRecommendationParameter(PlanRecordDTO):
    @property
    def prompt_format(self) -> str:
        sections = []
        if self.overall_plan is not None:
            sections.append(f"Plan Umum: {self.overall_plan}")
        if self.treatment is not None:
            sections.append(f"Tindakan: {self.treatment}")

        return "\n".join(sections)
