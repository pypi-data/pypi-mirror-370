from typing import List, Optional
from maleo.cds.schemas.data.coding.diagnosis import DiagnosisRecordSchema


# Exapanded diagnoses
ExpandedDiagnoses = DiagnosisRecordSchema
OptionalExpandedDiagnoses = Optional[ExpandedDiagnoses]
ListOfExpandedDiagnoses = List[ExpandedDiagnoses]
OptionalListOfExpandedDiagnoses = Optional[List[ExpandedDiagnoses]]
