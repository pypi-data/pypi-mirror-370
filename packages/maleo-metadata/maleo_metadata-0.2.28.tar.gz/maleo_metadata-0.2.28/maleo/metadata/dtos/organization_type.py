from maleo.soma.mixins.general import OptionalOrder
from maleo.metadata.mixins.organization_type import Key, Name


class OrganizationTypeDataDTO(
    Name,
    Key,
    OptionalOrder,
):
    pass
