from maleo.soma.mixins.general import IsRoot, IsParent, IsChild, IsLeaf
from maleo.soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfParentIds,
    OptionalListOfUuids,
    OptionalListOfCodes,
    OptionalListOfKeys,
    OptionalListOfNames,
)
from maleo.soma.schemas.parameter.client import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)
from maleo.metadata.mixins.medical_role import MedicalRoleId


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


class ReadMultipleRootSpecializationsParameter(
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleSpecializationsParameter(
    ReadMultipleRootSpecializationsParameter, MedicalRoleId
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


class ReadMultipleSpecializationsQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfNames,
    OptionalListOfKeys,
    OptionalListOfCodes,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
