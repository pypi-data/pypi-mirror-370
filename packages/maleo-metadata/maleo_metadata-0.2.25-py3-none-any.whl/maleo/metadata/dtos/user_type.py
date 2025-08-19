from maleo.soma.mixins.general import OptionalOrder
from maleo.metadata.mixins.user_type import Key, Name


class UserTypeDataDTO(
    Name,
    Key,
    OptionalOrder,
):
    pass
