from Crypto.PublicKey.RSA import RsaKey
from redis.asyncio.client import Redis
from typing import Optional
from maleo.soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo.soma.dtos.configurations.client.maleo import MaleoClientConfigurationDTO
from maleo.soma.managers.client.maleo import MaleoClientManager
from maleo.soma.managers.credential import CredentialManager
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import SimpleConfig
from maleo.metadata.client.services.blood_type import BloodTypeClientService
from maleo.metadata.client.services.gender import GenderClientService
from maleo.metadata.client.services.medical_role import MedicalRoleClientService
from maleo.metadata.client.services.organization_type import (
    OrganizationTypeClientService,
)
from maleo.metadata.client.services.service import ServiceClientService
from maleo.metadata.client.services.system_role import SystemRoleClientService
from maleo.metadata.client.services.user_type import UserTypeClientService


class ClientManager(MaleoClientManager):
    def __init__(
        self,
        configurations: MaleoClientConfigurationDTO,
        log_config: SimpleConfig,
        credential_manager: CredentialManager,
        private_key: RsaKey,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
        service_context: Optional[ServiceContext] = None,
    ):
        assert configurations.key == "maleo-metadata"
        assert configurations.name == "MaleoMetadata"
        super().__init__(
            configurations,
            log_config,
            credential_manager,
            private_key,
            redis,
            redis_namespaces,
            service_context,
        )
        self._initialize_services()
        self._logger.info("Client manager initialized successfully")

    def _initialize_services(self):
        self.blood_type = BloodTypeClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.gender = GenderClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.medical_role = MedicalRoleClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.organization_type = OrganizationTypeClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.service = ServiceClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.system_role = SystemRoleClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
        self.user_type = UserTypeClientService(
            environment=self._environment,
            key=self._key,
            url=self._url,
            operation_origin=self._operation_origin,
            logger=self._logger,
            credential_manager=self._credential_manager,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
            redis_namespaces=self._redis_namespaces,
            service_context=self._service_context,
        )
