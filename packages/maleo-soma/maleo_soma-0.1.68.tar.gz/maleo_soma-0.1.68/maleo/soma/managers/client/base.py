from typing import Optional
from maleo.soma.enums.cache import CacheLayer, CacheOrigin
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.operation import OperationLayer, OperationOrigin, OperationTarget
from maleo.soma.schemas.operation.context import OperationOriginSchema
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import ClientLogger, SimpleConfig


class ClientService:
    _OPERATION_LAYER_TYPE = OperationLayer.SERVICE
    _OPERATION_TARGET_TYPE = OperationTarget.INTERNAL
    _CACHE_ORIGIN = CacheOrigin.CLIENT
    _CACHE_LAYER = CacheLayer.SERVICE

    def __init__(
        self,
        service_context: ServiceContext,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
    ):
        self._service_context = service_context
        self._operation_origin = operation_origin
        self._logger = logger


class ClientManager:
    _OPERATION_ORIGIN_TYPE = OperationOrigin.CLIENT
    _CACHE_ORIGIN = CacheOrigin.CLIENT

    def __init__(
        self,
        key: str,
        name: str,
        log_config: SimpleConfig,
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        self._key = key
        self._name = name
        self._log_config = log_config

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self._operation_origin = OperationOriginSchema(
            type=self._OPERATION_ORIGIN_TYPE,
            details={"identifier": {"key": self._key, "name": self._name}},
        )

        self._logger = ClientLogger(
            client_key=self._key,
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            **self._log_config.model_dump(),
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def service_context(self) -> ServiceContext:
        return self._service_context

    @property
    def environment(self) -> Environment:
        raise NotImplementedError()

    @property
    def logger(self) -> ClientLogger:
        return self._logger

    @property
    def credentials(self):
        raise NotImplementedError()

    @property
    def client(self):
        raise NotImplementedError()
