from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.cds.dtos.coding.diagnosis import DiagnosisRecordDTO


class DiagnosisRecordSchema(
    DiagnosisRecordDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass
