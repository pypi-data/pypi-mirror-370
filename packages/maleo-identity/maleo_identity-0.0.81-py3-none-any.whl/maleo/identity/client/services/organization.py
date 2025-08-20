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
# from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
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
# from maleo.identity.constants.organization import RESOURCE as ORGANIZATION_RESOURCE
# from maleo.identity.schemas.data.organization_registration_code import (
#     OrganizationRegistrationCodeDataSchema,
# )
# from maleo.identity.schemas.data.organization_role import OrganizationRoleDataSchema
# from maleo.identity.schemas.data.organization import OrganizationDataSchema
# from maleo.identity.schemas.data.user_organization_role import (
#     UserOrganizationRoleDataSchema,
# )
# from maleo.identity.schemas.data.user_organization import UserOrganizationDataSchema
# from maleo.identity.schemas.parameter.client.organization_role import (
#     ReadMultipleFromOrganizationParameter as OrganizationRoleReadMultipleFromOrganizationParameter,
#     ReadMultipleFromOrganizationQueryParameter as OrganizationRoleReadMultipleFromOrganizationQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.organization import (
#     ReadMultipleParameter as OrganizationReadMultipleParameter,
#     ReadMultipleChildrenParameter as OrganizationReadMultipleChildrenParameter,
#     ReadMultipleQueryParameter as OrganizationReadMultipleQueryParameter,
#     ReadMultipleChildrenQueryParameter as OrganizationReadMultipleChildrenQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.user_organization_role import (
#     ReadMultipleFromUserOrganizationParameter as UserOrganizationRoleReadMultipleFromUserOrganizationParameter,
#     ReadMultipleFromUserOrganizationQueryParameter as UserOrganizationRoleReadMultipleFromUserOrganizationQueryParameter,
# )
# from maleo.identity.schemas.parameter.client.user_organization import (
#     ReadMultipleFromOrganizationParameter as UserOrganizationReadMultipleFromOrganizationParameter,
#     ReadMultipleFromOrganizationQueryParameter as UserOrganizationReadMultipleFromOrganizationQueryParameter,
# )
# from maleo.identity.schemas.parameter.general.organization_registration_code import (
#     ReadSingleParameter as OrganizationRegistrationCodeReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.organization_role import (
#     ReadSingleParameter as OrganizationRoleReadSingleParameter,
#     ReadSingleQueryParameter as OrganizationRoleReadSingleQueryParameter,
# )
# from maleo.identity.schemas.parameter.general.organization import (
#     ReadSingleQueryParameter as OrganizationReadSingleQueryParameter,
#     ReadSingleParameter as OrganizationReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.user_organization_role import (
#     ReadSingleQueryParameter as UserOrganizationRoleReadSingleQueryParameter,
#     ReadSingleParameter as UserOrganizationRoleReadSingleParameter,
# )
# from maleo.identity.schemas.parameter.general.user_organization import (
#     ReadSingleQueryParameter as UserOrganizationReadSingleQueryParameter,
#     ReadSingleParameter as UserOrganizationReadSingleParameter,
# )


# class OrganizationClientService(MaleoClientService):
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
#             ORGANIZATION_RESOURCE.aggregate(),
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

#     async def read_organizations(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationReadMultipleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         OrganizationDataSchema, StrictPagination, None
#     ]:
#         """Retrieve organizations from MaleoIdentity"""
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
#                     OrganizationDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organizations from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/"

#             # Parse parameters to query params
#             params = OrganizationReadMultipleQueryParameter.model_validate(
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
#                     OrganizationDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[OrganizationDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organizations from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[OrganizationDataSchema, None]:
#         """Retrieve organization from MaleoIdentity"""
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
#                     OrganizationDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[OrganizationDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.identifier}/{parameters.value}"

#             # Parse parameters to query params
#             params = OrganizationReadSingleQueryParameter.model_validate(
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
#                     OrganizationDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[OrganizationDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     OrganizationDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[OrganizationDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_children(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationReadMultipleChildrenParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         OrganizationDataSchema, StrictPagination, None
#     ]:
#         """Retrieve organizations from MaleoIdentity"""
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
#                     OrganizationDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organizations from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/children"

#             # Parse parameters to query params
#             params = OrganizationReadMultipleChildrenQueryParameter.model_validate(
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
#                     OrganizationDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[OrganizationDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organizations from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_registration_code(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationRegistrationCodeReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[
#         OrganizationRegistrationCodeDataSchema, None
#     ]:
#         """Retrieve organization registration code from MaleoIdentity"""
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
#                     OrganizationRegistrationCodeDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[
#                     OrganizationRegistrationCodeDataSchema, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization registration code from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.identifier}/{parameters.value}/registration-code"

#             # Parse parameters to query params
#             params = ReadSingleQueryParameterSchema.model_validate(
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
#                     OrganizationRegistrationCodeDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[OrganizationRegistrationCodeDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     OrganizationRegistrationCodeDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[
#                     OrganizationRegistrationCodeDataSchema, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization registration code from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_roles(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationRoleReadMultipleFromOrganizationParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         OrganizationRoleDataSchema, StrictPagination, None
#     ]:
#         """Retrieve organization roles from MaleoIdentity"""
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
#                     OrganizationRoleDataSchema, StrictPagination, None
#                 ].model_validate(json.loads(result_str))
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organization roles from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/roles/"

#             # Parse parameters to query params
#             params = OrganizationRoleReadMultipleFromOrganizationQueryParameter.model_validate(
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
#                     OrganizationRoleDataSchema, StrictPagination, None
#                 ].model_validate(response.json())
#                 data = DataPair[List[OrganizationRoleDataSchema], None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadMultipleResourceOperationResult[
#                     OrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadMultipleResourceOperationSchema[
#                     OrganizationRoleDataSchema, StrictPagination, None
#                 ](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved multiple organization roles from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_role(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: OrganizationRoleReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[OrganizationRoleDataSchema, None]:
#         """Retrieve organization role from MaleoIdentity"""
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
#                     OrganizationRoleDataSchema, None
#                 ].model_validate(json.loads(result_str))
#                 ReadSingleResourceOperationSchema[OrganizationRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization role from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/roles/{parameters.key}"

#             # Parse parameters to query params
#             params = OrganizationRoleReadSingleQueryParameter.model_validate(
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
#                     OrganizationRoleDataSchema, None
#                 ].model_validate(response.json())
#                 data = DataPair[OrganizationRoleDataSchema, None](
#                     old=validated_response.data,
#                     new=None,
#                 )
#                 result = ReadSingleResourceOperationResult[
#                     OrganizationRoleDataSchema, None
#                 ](
#                     data=data,
#                     pagination=validated_response.pagination,
#                     metadata=None,
#                     other=None,
#                 )
#                 ReadSingleResourceOperationSchema[OrganizationRoleDataSchema, None](
#                     service_context=self._service_context,
#                     id=operation_id,
#                     context=operation_context,
#                     timestamp=OperationTimestamp(
#                         executed_at=executed_at,
#                         completed_at=completed_at,
#                         duration=(completed_at - executed_at).total_seconds(),
#                     ),
#                     summary="Successfully retrieved single organization role from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_users(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationReadMultipleFromOrganizationParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadMultipleResourceOperationResult[
#         UserOrganizationDataSchema, StrictPagination, None
#     ]:
#         """Retrieve organization users from MaleoIdentity"""
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
#                     summary="Successfully retrieved multiple organization users from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/users/"

#             # Parse parameters to query params
#             params = UserOrganizationReadMultipleFromOrganizationQueryParameter.model_validate(
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
#                     summary="Successfully retrieved multiple organization users from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_user(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserOrganizationDataSchema, None]:
#         """Retrieve organization user from MaleoIdentity"""
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
#                     summary="Successfully retrieved single organization user from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/users/{parameters.user_id}"

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
#                     summary="Successfully retrieved single organization user from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_user_roles(
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
#         """Retrieve organization user roles from MaleoIdentity"""
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
#                     summary="Successfully retrieved multiple organization user roles from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(
#                     self._logger, level=LogLevel.INFO
#                 )
#                 return result

#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as http_client:
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/users/{parameters.user_id}/roles/"

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
#                     summary="Successfully retrieved multiple organization user roles from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )

#     async def read_organization_user_role(
#         self,
#         operation_id: UUID,
#         request_context: RequestContext,
#         authentication: Authentication,
#         parameters: UserOrganizationRoleReadSingleParameter,
#         authorization: Optional[Authorization] = None,
#         headers: Optional[Dict[str, str]] = None,
#     ) -> ReadSingleResourceOperationResult[UserOrganizationRoleDataSchema, None]:
#         """Retrieve organization user role from MaleoIdentity"""
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
#                     summary="Successfully retrieved single organization user role from cache",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
#                     result=result,
#                 ).log(self._logger, level=LogLevel.INFO)
#                 return result

#         # HTTP Request
#         operation_context = deepcopy(self._default_operation_context)
#         async with self._http_client_manager.get() as client:
#             # Define URL
#             url = f"{self._url}/v1/{ORGANIZATION_RESOURCE.identifiers[0].url_slug}/{parameters.organization_id}/users/{parameters.user_id}/roles/{parameters.key}"

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
#                     summary="Successfully retrieved single organization user role from http request",
#                     request_context=request_context,
#                     authentication=authentication,
#                     action=operation_action,
#                     resource=ORGANIZATION_RESOURCE,
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
#                 resource=ORGANIZATION_RESOURCE,
#             )
