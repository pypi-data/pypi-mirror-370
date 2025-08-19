from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.parameter.client import (
    ReadUnpaginatedMultipleParameterSchema,
    ReadUnpaginatedMultipleQueryParameterSchema,
)


class ReadMultipleParameter(
    ReadUnpaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleQueryParameter(
    ReadUnpaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
