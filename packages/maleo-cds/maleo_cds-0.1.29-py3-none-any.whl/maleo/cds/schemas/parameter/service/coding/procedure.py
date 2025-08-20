from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
    OptionalListOfCodes,
    Search,
)

from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema,
    Search,
    OptionalListOfCodes,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    Search,
    OptionalListOfCodes,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
