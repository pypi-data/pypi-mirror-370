from maleo.soma.mixins.general import OptionalOrder, OptionalParentId
from maleo.metadata.mixins.medical_role import Code, Key, Name


class MedicalRoleDataDTO(
    Name,
    Key,
    Code,
    OptionalOrder,
    OptionalParentId,
):
    pass
