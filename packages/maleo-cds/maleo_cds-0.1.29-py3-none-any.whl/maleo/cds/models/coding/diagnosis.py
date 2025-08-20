from sqlalchemy import Column, Enum, Float, Integer, Text, JSON
from maleo.soma.models.table import DataTable
from maleo.metadata.enums.gender import Gender
from maleo.cds.db import MaleoCDSBase


class CodingDiagnosesMixin:
    organization_id = Column(name="organization_id", type_=Integer)
    user_id = Column(name="user_id", type_=Integer, nullable=False)
    gender = Column(name="gender", type_=Enum(Gender, name="gender"))
    age = Column(name="age", type_=Integer)
    chief_complaint = Column(name="chief_complaint", type_=Text, nullable=False)
    additional_complaint = Column(name="additional_complaint", type_=Text)
    pain_scale = Column(name="pain_scale", type_=Integer)
    onset = Column(name="onset", type_=Text)
    chronology = Column(name="chronology", type_=Text)
    location = Column(name="location", type_=Text)
    aggravating_factor = Column(name="aggravating_factor", type_=Text)
    relieving_factor = Column(name="relieving_factor", type_=Text)
    personal_medical_history = Column(name="personal_medical_history", type_=Text)
    family_medical_history = Column(name="family_medical_history", type_=Text)
    habit_activity_occupation = Column(name="habit_activity_occupation", type_=Text)
    consumed_medication = Column(name="consumed_medication", type_=Text)
    systolic_blood_pressure = Column(name="systolic_blood_pressure", type_=Integer)
    diastolic_blood_pressure = Column(name="diastolic_blood_pressure", type_=Integer)
    temperature = Column(name="temperature", type_=Float)
    respiration_rate = Column(name="respiration_rate", type_=Integer)
    heart_rate = Column(name="heart_rate", type_=Integer)
    oxygen_saturation = Column(name="oxygen_saturation", type_=Integer)
    abdominal_circumference = Column(name="abdominal_circumference", type_=Float)
    waist_circumference = Column(name="waist_circumference", type_=Float)
    weight = Column(name="weight", type_=Float)
    height = Column(name="height", type_=Float)
    body_mass_index = Column(name="body_mass_index", type_=Float)
    organ_examination_detail = Column(name="organ_examination_detail", type_=Text)
    diagnoses = Column(name="diagnoses", type_=JSON)
    duration = Column(name="duration", type_=Float)


class CodingDiagnosesTable(CodingDiagnosesMixin, DataTable, MaleoCDSBase):
    __tablename__ = "coding_diagnoses"
