from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import OptionalOrder
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.service import ServiceDataDTO
from maleo.metadata.enums.service import IdentifierType
from maleo.metadata.mixins.service import (
    ServiceType,
    OptionalServiceType,
    Category,
    OptionalCategory,
    Name,
    OptionalName,
)
from maleo.metadata.types.base.service import IdentifierValueType


class CreateParameter(ServiceDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class PartialDataUpdateBody(
    OptionalName,
    OptionalServiceType,
    OptionalCategory,
    OptionalOrder,
):
    pass


class PartialDataUpdateParameter(
    PartialDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class FullDataUpdateBody(
    Name,
    ServiceType,
    Category,
    OptionalOrder,
):
    pass


class FullDataUpdateParameter(
    FullDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
