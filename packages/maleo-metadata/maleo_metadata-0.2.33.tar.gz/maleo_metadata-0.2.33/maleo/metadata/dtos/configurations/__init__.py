from maleo.soma.dtos.configurations import ConfigurationDTO as BaseConfigurationDTO
from maleo.soma.dtos.configurations.pubsub.publisher import TopicsConfigurationDTO


class ConfigurationDTO(BaseConfigurationDTO[None, TopicsConfigurationDTO, None]):
    pass
