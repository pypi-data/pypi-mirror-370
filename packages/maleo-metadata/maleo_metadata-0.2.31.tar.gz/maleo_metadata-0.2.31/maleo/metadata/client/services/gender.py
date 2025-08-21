import json
from copy import deepcopy
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timezone
from redis.asyncio.client import Redis
from typing import Dict, List, Literal, Optional, Union, overload
from uuid import UUID
from maleo.soma.authorization import BearerAuth
from maleo.soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo.soma.enums.cardinality import Cardinality
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.expiration import Expiration
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import OperationTarget
from maleo.soma.managers.client.maleo import MaleoClientService
from maleo.soma.managers.client.http import HTTPClientManager
from maleo.soma.managers.credential import CredentialManager
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.data import DataPair
from maleo.soma.schemas.operation.context import (
    OperationContextSchema,
    OperationOriginSchema,
    OperationLayerSchema,
    OperationTargetSchema,
)
from maleo.soma.schemas.operation.resource import (
    ReadSingleResourceOperationSchema,
    ReadMultipleResourceOperationSchema,
)
from maleo.soma.schemas.operation.resource.action import ReadResourceOperationAction
from maleo.soma.schemas.operation.resource.result import (
    ReadSingleResourceOperationResult,
    ReadMultipleResourceOperationResult,
)
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.pagination import FlexiblePagination
from maleo.soma.schemas.parameter.general import ReadSingleQueryParameterSchema
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.response import (
    SingleDataResponseSchema,
    MultipleDataResponseSchema,
)
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.cache import build_key
from maleo.soma.utils.logging import ClientLogger
from maleo.soma.utils.merger import merge_dicts
from maleo.soma.utils.token import reencode
from maleo.metadata.constants.gender import RESOURCE
from maleo.metadata.schemas.data.gender import GenderDataSchema
from maleo.metadata.schemas.parameter.client.gender import (
    ReadMultipleParameter,
    ReadMultipleQueryParameter,
)
from maleo.metadata.schemas.parameter.general.gender import ReadSingleParameter


class GenderClientService(MaleoClientService):
    def __init__(
        self,
        environment: Environment,
        key: str,
        url: str,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
        credential_manager: CredentialManager,
        http_client_manager: HTTPClientManager,
        private_key: RsaKey,
        redis: Redis,
        redis_namespaces: RedisCacheNamespaces,
        service_context: ServiceContext,
    ):
        super().__init__(
            environment,
            key,
            url,
            operation_origin,
            logger,
            credential_manager,
            http_client_manager,
            private_key,
            redis,
            redis_namespaces,
            service_context,
        )
        self._namespace = self._redis_namespaces.create(
            self._key,
            RESOURCE.aggregate(),
            origin=self._CACHE_ORIGIN,
            layer=self._CACHE_LAYER,
        )
        self._default_operation_context = OperationContextSchema(
            origin=self._operation_origin,
            layer=OperationLayerSchema(type=self._OPERATION_LAYER_TYPE, details=None),
            target=OperationTargetSchema(
                type=self._OPERATION_TARGET_TYPE, details=None
            ),
        )

    @overload
    async def read(
        self,
        cardinality: Literal[Cardinality.MULTIPLE],
        *,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        parameters: ReadMultipleParameter,
        headers: Optional[Dict[str, str]] = None,
    ) -> ReadMultipleResourceOperationResult[
        GenderDataSchema, FlexiblePagination, None
    ]: ...
    @overload
    async def read(
        self,
        cardinality: Literal[Cardinality.SINGLE],
        *,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        parameters: ReadSingleParameter,
        headers: Optional[Dict[str, str]] = None,
    ) -> ReadSingleResourceOperationResult[GenderDataSchema, None]: ...
    async def read(
        self,
        cardinality: Cardinality,
        *,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
        parameters: Union[ReadMultipleParameter, ReadSingleParameter],
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[
        ReadMultipleResourceOperationResult[GenderDataSchema, FlexiblePagination, None],
        ReadSingleResourceOperationResult[GenderDataSchema, None],
    ]:
        operation_action = ReadResourceOperationAction()
        executed_at = datetime.now(tz=timezone.utc)

        # Get function identifier
        func = self.__class__
        module, qualname = func.__module__, func.__qualname__

        # Define arguments being used in this function
        positional_arguments = [cardinality]
        keyword_arguments = {
            "authentication": authentication.model_dump(
                mode="json",
                exclude={
                    "credentials": {
                        "token": {
                            "payload": {
                                "iat_dt",
                                "iat",
                                "exp_dt",
                                "exp",
                            }
                        }
                    }
                },
            ),
            "parameters": parameters.model_dump(mode="json"),
        }

        # Define full function string
        function = f"{qualname}({json.dumps(positional_arguments)}|{json.dumps(keyword_arguments)})"

        # Define full cache key
        cache_key = build_key(module, function, namespace=self._namespace)

        if parameters.use_cache:
            operation_context = deepcopy(self._default_operation_context)
            operation_context.target.type = OperationTarget.CACHE

            # Check redis for data
            result_str = await self._redis.get(cache_key)

            if result_str is not None:
                completed_at = datetime.now(tz=timezone.utc)

                if isinstance(parameters, ReadMultipleParameter):
                    result = ReadMultipleResourceOperationResult[
                        GenderDataSchema, FlexiblePagination, None
                    ].model_validate(json.loads(result_str))
                    ReadMultipleResourceOperationSchema[
                        GenderDataSchema, FlexiblePagination, None
                    ](
                        service_context=self._service_context,
                        id=operation_id,
                        context=operation_context,
                        timestamp=OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ),
                        summary="Successfully retrieved multiple genders from cache",
                        request_context=request_context,
                        authentication=authentication,
                        action=operation_action,
                        resource=RESOURCE,
                        result=result,
                    ).log(
                        self._logger, LogLevel.INFO
                    )
                elif isinstance(parameters, ReadSingleParameter):
                    result = ReadSingleResourceOperationResult[
                        GenderDataSchema, None
                    ].model_validate(json.loads(result_str))
                    ReadSingleResourceOperationSchema[GenderDataSchema, None](
                        service_context=self._service_context,
                        id=operation_id,
                        context=operation_context,
                        timestamp=OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ),
                        summary="Successfully retrieved single gender from cache",
                        request_context=request_context,
                        authentication=authentication,
                        action=operation_action,
                        resource=RESOURCE,
                        result=result,
                    ).log(self._logger, LogLevel.INFO)
                return result

        operation_context = deepcopy(self._default_operation_context)
        async with self._http_client_manager.get() as http_client:
            # Create headers
            base_headers = {
                "Content-Type": "application/json",
                "X-Operation_Id": str(operation_id),
            }
            if headers is not None:
                headers = merge_dicts(base_headers, headers)
            else:
                headers = base_headers

            # Create auth
            token = None
            if authentication.credentials.token is not None:
                try:
                    token = reencode(
                        payload=authentication.credentials.token.payload,
                        key=self._private_key,
                    )
                except Exception:
                    pass

            auth = BearerAuth(token) if token is not None else None

            if isinstance(parameters, ReadMultipleParameter):
                # Define URL
                url = f"{self._url}/v1/{RESOURCE.identifiers[0].url_slug}/"

                # Parse parameters to query params
                params = ReadMultipleQueryParameter.model_validate(
                    parameters.model_dump()
                ).model_dump(
                    exclude={"sort_columns", "date_filters"}, exclude_none=True
                )
            elif isinstance(parameters, ReadSingleParameter):
                # Define URL
                url = f"{self._url}/v1/{RESOURCE.identifiers[0].url_slug}/{parameters.identifier}/{parameters.value}"

                # Parse parameters to query params
                params = ReadSingleQueryParameterSchema.model_validate(
                    parameters.model_dump()
                ).model_dump(exclude_none=True)

            # Send request and wait for response
            response = await http_client.get(
                url=url, params=params, headers=headers, auth=auth
            )

            if response.is_success:
                completed_at = datetime.now(tz=timezone.utc)

                if isinstance(parameters, ReadMultipleParameter):
                    validated_response = MultipleDataResponseSchema[
                        GenderDataSchema, FlexiblePagination, None
                    ].model_validate(response.json())
                    data = DataPair[List[GenderDataSchema], None](
                        old=validated_response.data,
                        new=None,
                    )
                    result = ReadMultipleResourceOperationResult[
                        GenderDataSchema, FlexiblePagination, None
                    ](
                        data=data,
                        pagination=validated_response.pagination,
                        metadata=None,
                        other=None,
                    )
                    ReadMultipleResourceOperationSchema[
                        GenderDataSchema, FlexiblePagination, None
                    ](
                        service_context=self._service_context,
                        id=operation_id,
                        context=operation_context,
                        timestamp=OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ),
                        summary="Successfully retrieved multiple genders from http request",
                        request_context=request_context,
                        authentication=authentication,
                        action=operation_action,
                        resource=RESOURCE,
                        result=result,
                    ).log(
                        self._logger, level=LogLevel.INFO
                    )
                elif isinstance(parameters, ReadSingleParameter):
                    validated_response = SingleDataResponseSchema[
                        GenderDataSchema, None
                    ].model_validate(response.json())
                    data = DataPair[GenderDataSchema, None](
                        old=validated_response.data,
                        new=None,
                    )
                    result = ReadSingleResourceOperationResult[GenderDataSchema, None](
                        data=data,
                        pagination=validated_response.pagination,
                        metadata=None,
                        other=None,
                    )
                    ReadSingleResourceOperationSchema[GenderDataSchema, None](
                        service_context=self._service_context,
                        id=operation_id,
                        context=operation_context,
                        timestamp=OperationTimestamp(
                            executed_at=executed_at,
                            completed_at=completed_at,
                            duration=(completed_at - executed_at).total_seconds(),
                        ),
                        summary="Successfully retrieved single gender from http request",
                        request_context=request_context,
                        authentication=authentication,
                        action=operation_action,
                        resource=RESOURCE,
                        result=result,
                    ).log(self._logger, level=LogLevel.INFO)

                if parameters.use_cache:
                    await self._redis.set(
                        cache_key, result.model_dump_json(), Expiration.EXP_1MO.value
                    )

                return result

            self._raise_resource_http_request_error(
                response=response,
                operation_id=operation_id,
                operation_context=operation_context,
                executed_at=executed_at,
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=RESOURCE,
            )
