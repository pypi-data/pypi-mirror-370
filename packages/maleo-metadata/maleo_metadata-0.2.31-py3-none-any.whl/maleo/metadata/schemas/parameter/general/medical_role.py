from maleo.soma.schemas.parameter.general import (
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.soma.mixins.general import OptionalParentId, OptionalOrder
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
)
from maleo.metadata.dtos.data.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.mixins.medical_role import Code, OptionalCode, Name, OptionalName
from maleo.metadata.types.base.medical_role import IdentifierValueType


class CreateParameter(MedicalRoleDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class FullDataUpdateBody(
    Name,
    Code,
    OptionalOrder,
    OptionalParentId,
):
    pass


class FullDataUpdateParameter(
    FullDataUpdateBody, IdentifierTypeValueMixin[IdentifierType, IdentifierValueType]
):
    pass


class PartialDataUpdateBody(
    OptionalName, OptionalCode, OptionalOrder, OptionalParentId
):
    pass


class PartialDataUpdateParameter(
    PartialDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateQueryParameterSchema,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
