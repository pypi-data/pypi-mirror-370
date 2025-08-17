from datetime import datetime, timezone
from uuid import UUID
from Crypto.PublicKey.RSA import RsaKey
from httpx import Response
from redis.asyncio.client import Redis
from typing import Optional
from maleo.soma.dtos.configurations.cache.redis import RedisCacheNamespaces
from maleo.soma.dtos.configurations.client.maleo import MaleoClientConfigurationDTO
from maleo.soma.enums.environment import Environment
from maleo.soma.exceptions import from_resource_http_request
from maleo.soma.managers.client.base import (
    ClientManager,
    ClientService,
)
from maleo.soma.managers.client.http import HTTPClientManager
from maleo.soma.managers.credential import CredentialManager
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.operation.context import (
    OperationContextSchema,
    OperationOriginSchema,
)
from maleo.soma.schemas.operation.resource.action import AllResourceOperationAction
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.resource import Resource
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import ClientLogger, SimpleConfig


class MaleoClientService(ClientService):
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
        super().__init__(service_context, operation_origin, logger)
        self._environment = environment
        self._key = key
        self._url = url
        self._credential_manager = credential_manager
        self._http_client_manager = http_client_manager
        self._private_key = private_key
        self._redis = redis
        self._redis_namespaces = redis_namespaces

    def _raise_resource_http_request_error(
        self,
        response: Response,
        operation_id: UUID,
        operation_context: OperationContextSchema,
        executed_at: datetime,
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext],
        authentication: Optional[Authentication],
        resource: Resource,
    ):
        """Handle HTTP error response and raise appropriate exception"""

        completed_at = datetime.now(tz=timezone.utc)
        timestamp = OperationTimestamp(
            executed_at=executed_at,
            completed_at=completed_at,
            duration=(completed_at - executed_at).total_seconds(),
        )

        error = from_resource_http_request(
            status_code=response.status_code,
            service_context=self._service_context,
            operation_id=operation_id,
            operation_context=operation_context,
            operation_timestamp=timestamp,
            operation_action=operation_action,
            request_context=request_context,
            authentication=authentication,
            resource=resource,
            logger=self._logger,
        )
        raise error


class MaleoClientManager(ClientManager):
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
        super().__init__(
            configurations.key,
            configurations.name,
            log_config,
            service_context,
        )
        self._environment = configurations.environment
        if (
            self._operation_origin.details is not None
            and "identifier" in self._operation_origin.details.keys()
            and isinstance(self._operation_origin.details["identifier"], dict)
        ):
            self._operation_origin.details["identifier"][
                "environment"
            ] = self._environment
        self._url = configurations.url
        self._http_client_manager = HTTPClientManager()
        self._credential_manager = credential_manager
        self._private_key = private_key
        self._redis = redis
        self._redis_namespaces = redis_namespaces
