from maleo.soma.mixins.general import OptionalOrder
from maleo.metadata.mixins.blood_type import Key, Name


class BloodTypeDataDTO(
    Name,
    Key,
    OptionalOrder,
):
    pass
