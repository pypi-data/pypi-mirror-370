from maleo.soma.mixins.general import OptionalOrder
from maleo.metadata.mixins.service import ServiceType, Category, Key, Name, Secret


class ServiceDataDTO(
    Name,
    Key,
    ServiceType,
    Category,
    OptionalOrder,
):
    pass


class FullServiceDataDTO(Secret, ServiceDataDTO):
    pass
