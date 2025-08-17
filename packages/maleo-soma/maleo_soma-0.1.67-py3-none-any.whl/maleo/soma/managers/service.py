from datetime import datetime, timezone
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from google.cloud import pubsub_v1
from google.oauth2.service_account import Credentials
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.types import Lifespan, AppType
from sqlalchemy import MetaData
from typing import Optional
from uuid import UUID
from maleo.soma.dtos.configurations import (
    ConfigurationDTO,
    LoggerDTO,
)
from maleo.soma.dtos.settings import Settings
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationLayer,
    OperationOrigin,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.exceptions import Error, InternalServerError
from maleo.soma.managers.cache import CacheManager
from maleo.soma.managers.db import DatabaseManager
from maleo.soma.managers.client.google.storage import GoogleCloudStorage
from maleo.soma.managers.middleware import MiddlewareManager
from maleo.soma.schemas.key.rsa import Complete
from maleo.soma.schemas.operation.context import (
    generate_operation_context,
)
from maleo.soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.utils.exceptions.request import (
    http_exception_handler,
    maleo_exception_handler,
    pydantic_validation_exception_handler,
    request_validation_exception_handler,
)
from maleo.soma.utils.logging import (
    SimpleConfig,
    ApplicationLogger,
    CacheLogger,
    DatabaseLogger,
    MiddlewareLogger,
    RepositoryLogger,
    ServiceLogger,
)
from maleo.soma.utils.name import get_fully_qualified_name


class ServiceManager:
    """ServiceManager class"""

    key = "service_manager"
    name = "ServiceManager"

    def __init__(
        self,
        operation_id: UUID,
        db_metadata: MetaData,
        google_credentials: Credentials,
        log_config: SimpleConfig,
        settings: Settings,
        configurations: ConfigurationDTO,
        keys: Complete,
    ):
        self._db_metadata = db_metadata
        self._google_credentials = google_credentials
        self._log_config = log_config
        self._settings = settings
        self._configurations = configurations
        self._keys = keys

        # Initialize Service Context
        self._service_context = self._settings.service_context

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

        self._initialize_loggers()

        try:
            self._initialize_database_manager(operation_id=operation_id)
            self._initialize_publisher()
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
            ).log(logger=self.loggers.application, level=LogLevel.INFO)
        except Error:
            raise
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Exception raised when initializing {self.name}",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            ) from e

    def _initialize_loggers(self) -> None:
        application = ApplicationLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        cache = CacheLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        database = DatabaseLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        middleware = MiddlewareLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        repository = RepositoryLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        service = ServiceLogger(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            **self._log_config.model_dump(),
        )
        self.loggers = LoggerDTO(
            application=application,
            cache=cache,
            database=database,
            middleware=middleware,
            repository=repository,
            service=service,
        )

    async def initialize_cache_manager(self) -> None:
        self.cache_manager = await CacheManager.new(
            settings=self._settings, configurations=self._configurations.cache
        )

    def initialize_cloud_storage(self, operation_id: UUID) -> None:
        environment = (
            Environment.STAGING
            if self._settings.ENVIRONMENT == Environment.LOCAL
            else self._settings.ENVIRONMENT
        )
        self.cloud_storage = GoogleCloudStorage(
            log_config=self._log_config,
            service_context=self._service_context,
            operation_id=operation_id,
            bucket_name=f"maleo-suite-{environment}",
            credentials=self._google_credentials,
            redis=self.cache_manager.redis,
        )

    def _initialize_database_manager(self, operation_id: UUID) -> None:
        self.database_manager = DatabaseManager(
            metadata=self._db_metadata,
            logger=self.loggers.database,
            url=self._configurations.database.url,
            service_context=self._service_context,
            operation_id=operation_id,
        )

    def _initialize_publisher(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()

    def create_app(
        self,
        operation_id: UUID,
        router: APIRouter,
        lifespan: Optional[Lifespan[AppType]] = None,
        version: str = "unknown",
    ) -> FastAPI:
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
            details={"type": "app_creation"},
        )

        executed_at = datetime.now(tz=timezone.utc)

        try:
            root_path = self._settings.ROOT_PATH
            self.app = FastAPI(
                title=self._configurations.service.name,
                version=version,
                lifespan=lifespan,  # type: ignore
                root_path=root_path,
            )

            # Add middleware(s)
            self.middleware_manager = MiddlewareManager(
                self.app,
                operation_id=operation_id,
                configuration=self._configurations.middleware,
                keys=self._keys,
                logger=self.loggers.middleware,
                service_context=self._service_context,
            )
            self.middleware_manager.add(operation_id=operation_id)

            # Add exception handler(s)
            self.app.add_exception_handler(
                exc_class_or_status_code=ValidationError,
                handler=pydantic_validation_exception_handler,  # type: ignore
            )
            self.app.add_exception_handler(
                exc_class_or_status_code=RequestValidationError,
                handler=request_validation_exception_handler,  # type: ignore
            )
            self.app.add_exception_handler(
                exc_class_or_status_code=HTTPException,
                handler=http_exception_handler,  # type: ignore
            )
            self.app.add_exception_handler(
                exc_class_or_status_code=Error,
                handler=maleo_exception_handler,  # type: ignore
            )

            # Include router
            self.app.include_router(router)

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
                summary="Successfully created FastAPI application",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self.loggers.application, level=LogLevel.INFO)

            return self.app
        except Error:
            raise
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Exception raised when creating FastAPI application",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            ) from e

    async def dispose(self, operation_id: UUID) -> None:

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
            type=SystemOperationType.DISPOSAL, details=None
        )

        if self.cache_manager.redis is not None:
            await self.cache_manager.redis.close()
        if self.database_manager is not None:
            self.database_manager.dispose(operation_id)
        if self.loggers is not None:
            self.loggers.application.dispose()
            self.loggers.database.dispose()
            self.loggers.middleware.dispose()

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=None,
            ),
            summary="Successfully disposed ServiceManager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self.loggers.application, level=LogLevel.INFO)
