from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import OptionalOrder
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.user_type import UserTypeDataDTO
from maleo.metadata.enums.user_type import IdentifierType
from maleo.metadata.mixins.user_type import Name, OptionalName
from maleo.metadata.types.base.user_type import IdentifierValueType


class CreateParameter(UserTypeDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class FullUpdateBody(
    Name,
    OptionalOrder,
):
    pass


class FullUpdateParameter(
    FullUpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class PartialUpdateBody(
    OptionalName,
    OptionalOrder,
):
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
