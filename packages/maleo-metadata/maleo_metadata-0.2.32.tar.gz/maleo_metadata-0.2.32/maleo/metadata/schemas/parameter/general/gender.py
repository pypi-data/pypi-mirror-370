from maleo.soma.schemas.parameter.general import (
    ReadSingleParameterSchema,
    StatusUpdateQueryParameterSchema,
)
from maleo.soma.mixins.general import OptionalOrder
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
)
from maleo.metadata.enums.gender import IdentifierType
from maleo.metadata.mixins.gender import Name, OptionalName
from maleo.metadata.types.base.gender import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class FullDataUpdateBody(
    Name,
    OptionalOrder,
):
    pass


class FullDataUpdateParameter(
    FullDataUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class PartialDataUpdateBody(
    OptionalName,
    OptionalOrder,
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
