from pydantic import BaseModel, Field
from maleo.soma.mixins.timestamp import Duration


class DisclaimerMetadataSchema(BaseModel):
    en: str = (
        "The completeness of subjective and objective data greatly influences the results of recommendations from Clinical Decision Support"
    )
    id: str = (
        "Kelengkapan data subjektif dan objektif sangat mempengaruhi hasil rekomendasi dari Clinical Decision Support"
    )


class GenerateDifferentialDiagnosesMetadataSchema(Duration):
    disclaimer: DisclaimerMetadataSchema = Field(
        default_factory=DisclaimerMetadataSchema, description="Disclaimer"
    )
