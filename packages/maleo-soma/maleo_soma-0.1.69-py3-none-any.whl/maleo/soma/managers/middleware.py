from datetime import datetime, timezone
from fastapi import FastAPI
from typing import Optional
from uuid import UUID
from maleo.soma.dtos.configurations.middleware import MiddlewareConfigurationDTO
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationLayer,
    OperationOrigin,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.middlewares.authentication import add_authentication_middleware
from maleo.soma.middlewares.base import add_base_middleware
from maleo.soma.middlewares.cors import add_cors_middleware
from maleo.soma.middlewares.rate_limit import RateLimiter
from maleo.soma.middlewares.response_builder import ResponseBuilder
from maleo.soma.middlewares.state import add_state_middleware
from maleo.soma.schemas.key.rsa import Complete
from maleo.soma.schemas.operation.context import generate_operation_context
from maleo.soma.schemas.operation.system import SuccessfulSystemOperationSchema
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import MiddlewareLogger
from maleo.soma.utils.name import get_fully_qualified_name


class MiddlewareManager:
    """MiddlewareManager class"""

    key = "middleware_manager"
    name = "MiddlewareManager"

    def __init__(
        self,
        app: FastAPI,
        *,
        operation_id: UUID,
        configuration: MiddlewareConfigurationDTO,
        keys: Complete,
        logger: MiddlewareLogger,
        service_context: Optional[ServiceContext] = None,
    ):
        self._app = app
        self._configuration = configuration
        self._keys = keys
        self._logger = logger

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "manager_initialization",
                "manager_key": self.key,
                "manager_name": self.name,
            },
        )

        executed_at = datetime.now(tz=timezone.utc)

        self.rate_limiter = RateLimiter(
            operation_id=operation_id,
            configuration=self._configuration.rate_limiter,
            logger=self._logger,
            service_context=self._service_context,
        )

        self._response_builder = ResponseBuilder(
            logger=self._logger,
            private_key=self._keys.private_rsa_key,
            service_context=self._service_context,
            operation_id=operation_id,
        )

        completed_at = datetime.now(tz=timezone.utc)
        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary=f"Successfully initialized {self.name}",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    def add(self, operation_id: UUID):
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            layer_details={
                "component": {"key": self.key, "name": self.name},
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.STARTUP,
            details={"type": "middlewares_addition"},
        )

        executed_at = datetime.now(tz=timezone.utc)

        add_base_middleware(
            self._app,
            logger=self._logger,
            private_key=self._keys.private_rsa_key,
            rate_limiter=self.rate_limiter,
            response_builder=self._response_builder,
            service_context=self._service_context,
            operation_id=operation_id,
        )
        add_state_middleware(
            self._app,
            logger=self._logger,
            service_context=self._service_context,
            operation_id=operation_id,
        )
        add_authentication_middleware(self._app, public_key=self._keys.public_rsa_key)
        add_cors_middleware(self._app, configuration=self._configuration.cors)

        completed_at = datetime.now(tz=timezone.utc)
        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary="Successfully added all middlewares to FastAPI application",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)
