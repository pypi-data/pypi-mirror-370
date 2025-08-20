# import json
# from copy import deepcopy
# from Crypto.PublicKey.RSA import RsaKey
# from datetime import datetime, timezone
# from redis.asyncio.client import Redis
# from typing import Dict, List, Optional
# from uuid import UUID
# from maleo.soma.authorization import BearerAuth
# from maleo.soma.dtos.configurations.cache.redis import RedisCacheNamespaces
# from maleo.soma.enums.environment import Environment
# from maleo.soma.enums.expiration import Expiration
# from maleo.soma.enums.logging import LogLevel
# from maleo.soma.enums.operation import OperationTarget
# from maleo.soma.managers.client.maleo import MaleoClientService
# from maleo.soma.managers.client.http import HTTPClientManager
# from maleo.soma.managers.credential import CredentialManager
# from maleo.soma.schemas.authentication import Authentication
# from maleo.soma.schemas.authorization import Authorization
# from maleo.soma.schemas.data import DataPair
# from maleo.soma.schemas.operation.context import (
#     OperationContextSchema,
#     OperationOriginSchema,
#     OperationLayerSchema,
#     OperationTargetSchema,
# )
# from maleo.soma.schemas.operation.resource import (
#     ReadSingleResourceOperationSchema,
#     ReadMultipleResourceOperationSchema,
# )
# from maleo.soma.schemas.operation.resource.action import ReadResourceOperationAction
# from maleo.soma.schemas.operation.resource.result import (
#     ReadSingleResourceOperationResult,
#     ReadMultipleResourceOperationResult,
# )
# from maleo.soma.schemas.operation.timestamp import OperationTimestamp
# from maleo.soma.schemas.pagination import StrictPagination
# from maleo.soma.schemas.request import RequestContext
# from maleo.soma.schemas.response import (
#     SingleDataResponseSchema,
#     MultipleDataResponseSchema,
# )
# from maleo.soma.schemas.service import ServiceContext
# from maleo.soma.utils.cache import build_key
# from maleo.soma.utils.logging import ClientLogger
# from maleo.soma.utils.merger import merge_dicts
# from maleo.soma.utils.token import reencode
# from maleo.identity.constants.user import RESOURCE as USER_RESOURCE
# from maleo.identity.schemas.data.user_organization_role import (
#     UserOrganizationRoleDataSchema,
# )
# from maleo.identity.schemas.data.user_organization import UserOrganizationDataSchema
# from maleo.identity.schemas.data.user_system_role import UserSystemRoleDataSchema
# from maleo.identity.schemas.data.user import UserDataSchema
# from maleo.identity.schemas.parameter.client.user_organization_role import (
#     ReadMultipleFromUserOrganizationParameter as UserOrganizationRoleReadMultipleFromUserOrganizationParameter,
#     ReadMultipleFromUserOrganizationQueryParameter as UserOrganizationRoleReadMultipleFromUserOrganizationQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.user_organization import (
#     ReadMultipleFromUserParameter as UserOrganizationReadMultipleFromUserParameter,
#     ReadMultipleFromUserQueryParameter as UserOrganizationReadMultipleFromUserQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.user_system_role import (
#     ReadMultipleFromUserParameter as UserSystemRoleReadMultipleFromUserParameter,
#     ReadMultipleFromUserQueryParameter as UserSystemRoleReadMultipleFromUserQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.user import (
#     ReadMultipleParameter as UserReadMultipleParameter,
#     ReadMultipleQueryParameter as UserReadMultipleQueryParameter,
# )
# from maleo.identity.schemas.parameter.general.user_organization_role import (
#     ReadSingleQueryParameter as UserOrganizationRoleReadSingleQueryParameter,
#     ReadSingleParameter as UserOrganizationRoleReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.user_organization import (
#     ReadSingleQueryParameter as UserOrganizationReadSingleQueryParameter,
#     ReadSingleParameter as UserOrganizationReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.user_system_role import (
#     ReadSingleQueryParameter as UserSystemRoleReadSingleQueryParameter,
#     ReadSingleParameter as UserSystemRoleReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.user import (
#     ReadSingleQueryParameter as UserReadSingleQueryParameter,
#     ReadSingleParameter as UserReadSingleParameter,
# )


# class UserClientService(MaleoClientService):
#     def __init__(
#         self,
#         environment: Environment,
#         key: str,
#         url: str,
#         operation_origin: OperationOriginSchema,
#         logger: ClientLogger,
#         credential_manager: CredentialManager,
#         http_client_manager: HTTPClientManager,
#         private_key: RsaKey,
#         redis: Redis,
#         redis_namespaces: RedisCacheNamespaces,
#         service_context: ServiceContext,
#     ):
#         super().__init__(
#             environment,
#             key,
#             url,
#             operation_origin,
#             logger,
#             credential_manager,
#             http_client_manager,
#             private_key,
#             redis,
#             redis_namespaces,
#             service_context,
#         )
#         # self._controllers = controllers
#         self._namespace = self._redis_namespaces.create(
#             self._key,
#             USER_RESOURCE.aggregate(),
#             origin=self._CACHE_ORIGIN,
#             layer=self._CACHE_LAYER,
#         )
#         self._default_operation_context = OperationContextSchema(
#             origin=self._operation_origin,
#             layer=OperationLayerSchema(type=self._OPERATION_LAYER_TYPE, details=None),
#             target=OperationTargetSchema(
#                 type=self._OPERATION_TARGET_TYPE, details=None
#             ),
#         )

#     async def read_users(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserReadMultipleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[UserDataSchema, StrictPagination, None]:
#         """Retrieve users from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE

#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadMultipleResourceOperationResult[
#                     UserDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     UserDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple users from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/"

#             # Parse parameters to query params
#             params = UserReadMultipleQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude={"sort_columns", "date_filters"}, exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await http_client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = MultipleDataResponseSchema[
#                     UserDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[UserDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     UserDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     UserDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple users from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserDataSchema, None]:
#         """Retrieve user from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             # Cache operation
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE
#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadSingleResourceOperationResult[
#                     UserDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[UserDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.identifier}/{parameters.value}"

#             # Parse parameters to query params
#             params = UserReadSingleQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = SingleDataResponseSchema[
#                     UserDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[UserDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[UserDataSchema, None](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[UserDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_organizations(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationReadMultipleFromUserParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         UserOrganizationDataSchema, StrictPagination, None
#     ]:
#         """Retrieve user organizations from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE

#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadMultipleResourceOperationResult[
#                     UserOrganizationDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     UserOrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user organizations from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/organizations/"

#             # Parse parameters to query params
#             params = UserOrganizationReadMultipleFromUserQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude={"sort_columns", "date_filters"}, exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await http_client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = MultipleDataResponseSchema[
#                     UserOrganizationDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[UserOrganizationDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     UserOrganizationDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     UserOrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user organizations from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_organization(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserOrganizationDataSchema, None]:
#         """Retrieve user organization from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             # Cache operation
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE
#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadSingleResourceOperationResult[
#                     UserOrganizationDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[UserOrganizationDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user organization from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/organizations/{parameters.organization_id}"

#             # Parse parameters to query params
#             params = UserOrganizationReadSingleQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = SingleDataResponseSchema[
#                     UserOrganizationDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[UserOrganizationDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     UserOrganizationDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[UserOrganizationDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user organization from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_organization_roles(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationRoleReadMultipleFromUserOrganizationParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         UserOrganizationRoleDataSchema, StrictPagination, None
#     ]:
#         """Retrieve user organization roles from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE

#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadMultipleResourceOperationResult[
#                     UserOrganizationRoleDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     UserOrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user organization roles from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/organizations/{parameters.organization_id}/roles/"

#             # Parse parameters to query params
#             params = UserOrganizationRoleReadMultipleFromUserOrganizationQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(
#                 exclude={"sort_columns", "date_filters"}, exclude_none=True
#             )

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await http_client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = MultipleDataResponseSchema[
#                     UserOrganizationRoleDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[UserOrganizationRoleDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     UserOrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     UserOrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user organization roles from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_organization_role(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationRoleReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserOrganizationRoleDataSchema, None]:
#         """Retrieve user organization role from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             # Cache operation
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE
#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadSingleResourceOperationResult[
#                     UserOrganizationRoleDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[UserOrganizationRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user organization role from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/organizations/{parameters.organization_id}/roles/{parameters.key}"

#             # Parse parameters to query params
#             params = UserOrganizationRoleReadSingleQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = SingleDataResponseSchema[
#                     UserOrganizationRoleDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[UserOrganizationRoleDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     UserOrganizationRoleDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[UserOrganizationRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user organization role from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_system_roles(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserSystemRoleReadMultipleFromUserParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         UserSystemRoleDataSchema, StrictPagination, None
#     ]:
#         """Retrieve user system roles from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE

#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadMultipleResourceOperationResult[
#                     UserSystemRoleDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     UserSystemRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user system roles from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/system-roles/"

#             # Parse parameters to query params
#             params = UserSystemRoleReadMultipleFromUserQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude={"sort_columns", "date_filters"}, exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await http_client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = MultipleDataResponseSchema[
#                     UserSystemRoleDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[UserSystemRoleDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     UserSystemRoleDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     UserSystemRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple user system roles from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )

#     async def read_user_system_role(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserSystemRoleReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserSystemRoleDataSchema, None]:
#         """Retrieve user system role from MaleoIdentity"""
#         operation_action = ReadResourceOperationAction()
#         executed_at = datetime.now(tz=timezone.utc)

#         # Get function identifier
#         func = self.__class__
#         module, qualname = func.__module__, func.__qualname__

#         # Define arguments being used in this function
#         positional_arguments = []
#         keyword_arguments = {
#             "authentication": authentication.model_dump(
#                 mode="json",
#                 exclude={
#                     "credentials": {
#                         "token": {
#                             "payload": {
#                                 "iat_dt",
#                                 "iat",
#                                 "exp_dt",
#                                 "exp",
#                             }
#                         }
#                     }
#                 },
#             ),
#             "parameters": parameters.model_dump(mode="json"),
#         }

#         # Define full function string
#         function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

#         # Define full cache key
#         cache_key = build_key(module, function, namespace=self._namespace)

#         if parameters.use_cache:
#             # Cache operation
#             operation_context = deepcopy(self._default_operation_context)
#             operation_context.target.type = OperationTarget.CACHE
#             # Check redis for data
#             result_str = await self._redis.get(cache_key)

#             if result_str is not None:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 result = ReadSingleResourceOperationResult[
#                     UserSystemRoleDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[UserSystemRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user system role from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{USER_RESOURCE.identifiers[0].url_slug}/{parameters.user_id}/system-roles/{parameters.system_role}"

#             # Parse parameters to query params
#             params = UserSystemRoleReadSingleQueryParameter.model_validate(
#                 parameters.model_dump()
#             ).model_dump(exclude_none=True)

#             # Create headers
#             base_headers = {
#                 "Content-Type": "application/json",
#                 "X-Operation_Id": str(operation_id),
#             }
#             if headers is not None:
#                 headers = merge_dicts(base_headers, headers)
#             else:
#                 headers = base_headers

#             # Create auth
#             token = None
#             if authentication.credentials.token is not None:
#                 try:
#                     token = reencode(
#                         payload=authentication.credentials.token.payload,
#                         key=self._private_key,
#                     )
#                 except Exception:
#                     pass

#             if (
#                 token is None
#                 and authorization is not None
#                 and authorization.scheme == "Bearer"
#             ):
#                 token = authorization.credentials

#             if token is None:
#                 token = self._credential_manager.token

#             auth = BearerAuth(token) if token is not None else None

#             # Send request and wait for response
#             response = await client.get(
#                 url=url, params=params, headers=headers, auth=auth
#             )

#             if response.is_success:
#                 completed_at = datetime.now(tz=timezone.utc)
#                 validated_response = SingleDataResponseSchema[
#                     UserSystemRoleDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[UserSystemRoleDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     UserSystemRoleDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[UserSystemRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single user system role from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=USER_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)

#                 if parameters.use_cache:
#                     await self._redis.set(
#                         cache_key, result.model_dump_json(), Expiration.EXP_1WK
#                     )

#                 return result

#             self._raise_resource_http_request_error(
#                 response=response,
#                 operation_id=operation_id,
#                 operation_context=operation_context,
#                 executed_at=executed_at,
#                 operation_action=operation_action,
#                 request_context=request_context,
#                 authentication=authentication,
#                 resource=USER_RESOURCE,
#             )
