from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import OptionalParentId, OptionalOrder
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.mixins.medical_role import Code, OptionalCode, Name, OptionalName
from maleo.metadata.types.base.medical_role import IdentifierValueType


class CreateParameter(MedicalRoleDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class FullUpdateBody(
    Name,
    Code,
    OptionalOrder,
    OptionalParentId,
):
    pass


class FullUpdateParameter(
    FullUpdateBody, IdentifierTypeValueMixin[IdentifierType, IdentifierValueType]
):
    pass


class PartialUpdateBody(OptionalName, OptionalCode, OptionalOrder, OptionalParentId):
    pass


class PartialUpdateParameter(
    PartialUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
