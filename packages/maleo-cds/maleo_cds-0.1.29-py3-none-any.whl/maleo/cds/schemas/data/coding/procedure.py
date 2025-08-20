from maleo.soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo.cds.dtos.coding.procedure import ProcedureRecordDTO


class ProcedureRecordSchema(
    ProcedureRecordDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass
