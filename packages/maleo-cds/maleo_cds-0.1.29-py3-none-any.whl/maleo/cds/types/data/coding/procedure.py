from typing import List, Optional
from maleo.cds.schemas.data.coding.procedure import ProcedureRecordSchema


# Exapanded procedures
ExpandedProcedures = ProcedureRecordSchema
OptionalExpandedProcedures = Optional[ExpandedProcedures]
ListOfExpandedProcedures = List[ExpandedProcedures]
OptionalListOfExpandedProcedures = Optional[List[ExpandedProcedures]]
