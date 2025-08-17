from maleo.soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfCodes,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.parameter.service import (
    ReadPaginatedMultipleQueryParameterSchema,
    ReadPaginatedMultipleParameterSchema,
)


class ReadMultipleSpecializationsQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    IsLeaf,
    IsChild,
    IsParent,
    IsRoot,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
