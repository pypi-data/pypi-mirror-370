# from Crypto.PublicKey.RSA import RsaKey
# from redis.asyncio.client import Redis
# from typing import Optional
# from maleo.soma.dtos.configurations.cache.redis import RedisCacheNamespaces
# from maleo.soma.dtos.configurations.client.maleo import MaleoClientConfigurationDTO
# from maleo.soma.managers.client.maleo import MaleoClientManager
# from maleo.soma.managers.credential import CredentialManager
# from maleo.soma.schemas.service import ServiceContext
# from maleo.soma.utils.logging import SimpleConfig
# from maleo.identity.client.services.organization_registration_code import (
#     OrganizationRegistrationCodeClientService,
# )
# from maleo.identity.client.services.organization_role import (
#     OrganizationRoleClientService,
# )
# from maleo.identity.client.services.organization import OrganizationClientService
# from maleo.identity.client.services.user_organization_role import (
#     UserOrganizationRoleClientService,
# )
# from maleo.identity.client.services.user_organization import (
#     UserOrganizationClientService,
# )
# from maleo.identity.client.services.user_profile import UserProfileClientService
# from maleo.identity.client.services.user_system_role import UserSystemRoleClientService
# from maleo.identity.client.services.user import UserClientService


# class ClientManager(MaleoClientManager):
#     def __init__(
#         self,
#         configurations: MaleoClientConfigurationDTO,
#         log_config: SimpleConfig,
#         credential_manager: CredentialManager,
#         private_key: RsaKey,
#         redis: Redis,
#         redis_namespaces: RedisCacheNamespaces,
#         service_context: Optional[ServiceContext] = None,
#     ):
#         assert configurations.key == "maleo-identity"
#         assert configurations.name == "MaleoIdentity"
#         super().__init__(
#             configurations,
#             log_config,
#             credential_manager,
#             private_key,
#             redis,
#             redis_namespaces,
#             service_context,
#         )
#         self._initialize_services()
#         self._logger.info("Client manager initialized successfully")

#     def _initialize_services(self):
#         self.organization_registration_code = OrganizationRegistrationCodeClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.organization_role = OrganizationRoleClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.organization = OrganizationClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.user_organization_role = UserOrganizationRoleClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.user_organization = UserOrganizationClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.user_profile = UserProfileClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.user_system_role = UserSystemRoleClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
#         self.user = UserClientService(
#             environment=self._environment,
#             key=self._key,
#             url=self._url,
#             operation_origin=self._operation_origin,
#             logger=self._logger,
#             credential_manager=self._credential_manager,
#             http_client_manager=self._http_client_manager,
#             private_key=self._private_key,
#             redis=self._redis,
#             redis_namespaces=self._redis_namespaces,
#             service_context=self._service_context,
#         )
