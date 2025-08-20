from pydantic import BaseModel, Field
from maleo.soma.types.base import (
    OptionalFloat,
    OptionalInteger,
    OptionalString,
)


class Reasoning(BaseModel):
    reasoning: str = Field(..., description="Specific reasoning")


class OptionalReasoning(BaseModel):
    reasoning: OptionalString = Field(
        None, description="Specific reasoning. (Optional)"
    )


class ChiefComplaint(BaseModel):
    chief_complaint: str = Field(..., description="Patient's chief complaint")


class OptionalAdditionalComplaint(BaseModel):
    additional_complaint: OptionalString = Field(
        None, description="Patient's additional complaint"
    )


class OptionalPainScale(BaseModel):
    pain_scale: OptionalInteger = Field(
        None, ge=1, le=10, description="Patient's pain scale"
    )


class OptionalOnset(BaseModel):
    onset: OptionalString = Field(None, description="Patient's onset")


class OptionalChronology(BaseModel):
    chronology: OptionalString = Field(None, description="Patient's chronology")


class OptionalLocation(BaseModel):
    location: OptionalString = Field(None, description="Patient's location")


class OptionalAggravatingFactor(BaseModel):
    aggravating_factor: OptionalString = Field(
        None, description="Patient's aggravating factor"
    )


class OptionalRelievingFactor(BaseModel):
    relieving_factor: OptionalString = Field(
        None, description="Patient's relieving factor"
    )


class OptionalPersonalMedicalHistory(BaseModel):
    personal_medical_history: OptionalString = Field(
        None, description="Patient's personal medical history"
    )


class OptionalFamilyMedicalHistory(BaseModel):
    family_medical_history: OptionalString = Field(
        None, description="Patient's family medical history"
    )


class OptionalHabitActivityOccupation(BaseModel):
    habit_activity_occupation: OptionalString = Field(
        None, description="Patient's habit activity occupation"
    )


class OptionalConsumedMedication(BaseModel):
    consumed_medication: OptionalString = Field(
        None, description="Patient's consumed medication"
    )


class OptionalSystolicBloodPressure(BaseModel):
    systolic_blood_pressure: OptionalInteger = Field(
        None, ge=1, description="Patient's systolic blood pressure"
    )


class OptionalDiastolicBloodPressure(BaseModel):
    diastolic_blood_pressure: OptionalInteger = Field(
        None, ge=1, description="Patient's diastolic blood pressure"
    )


class OptionalTemperature(BaseModel):
    temperature: OptionalFloat = Field(None, ge=1, description="Patient's temperature")


class OptionalRespirationRate(BaseModel):
    respiration_rate: OptionalInteger = Field(
        None, ge=1, description="Patient's respiration rate"
    )


class OptionalHeartRate(BaseModel):
    heart_rate: OptionalInteger = Field(None, ge=1, description="Patient's heart rate")


class OptionalOxygenSaturation(BaseModel):
    oxygen_saturation: OptionalInteger = Field(
        None, le=100, description="Patient's oxygen saturation"
    )


class OptionalAbdominalCircumference(BaseModel):
    abdominal_circumference: OptionalFloat = Field(
        None, description="Patient's abdominal circumference"
    )


class OptionalWaistCircumference(BaseModel):
    waist_circumference: OptionalFloat = Field(
        None, description="Patient's waist circumference"
    )


class OptionalWeight(BaseModel):
    weight: OptionalFloat = Field(None, ge=1, description="Patient's weight")


class OptionalHeight(BaseModel):
    height: OptionalFloat = Field(None, ge=1, description="Patient's height")


class OptionalBodyMassIndex(BaseModel):
    body_mass_index: OptionalFloat = Field(
        None, description="Patient's body mass index"
    )


class OptionalOrganExaminationDetail(BaseModel):
    organ_examination_detail: OptionalString = Field(
        None, description="Patient's organ examination details"
    )


class OptionalOverallPlan(BaseModel):
    overall_plan: OptionalString = Field(None, description="Patient's overall plan")


class OptionalTreatment(BaseModel):
    treatment: OptionalString = Field(None, description="Patient's treatment")
