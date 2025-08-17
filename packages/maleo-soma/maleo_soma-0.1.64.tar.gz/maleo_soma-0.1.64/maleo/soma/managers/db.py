import os
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import MetaData, text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Any, Generator, Optional, Type
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationOrigin,
    OperationLayer,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.exceptions import (
    InternalServerError,
    DatabaseError,
)
from maleo.soma.models.table import BaseTable
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.operation.context import generate_operation_context
from maleo.soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalString
from maleo.soma.utils.logging import DatabaseLogger


def create_base(cls: Type[Any] = BaseTable) -> DeclarativeMeta:
    return declarative_base(cls=cls)


class SessionManager:
    def __init__(
        self,
        engine: Engine,
        *,
        operation_id: UUID,
        logger: DatabaseLogger,
        service_context: Optional[ServiceContext] = None,
    ):
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            target=OperationTarget.DATABASE,
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)

        try:
            self._sessionmaker: sessionmaker[Session] = sessionmaker(
                bind=engine, expire_on_commit=False
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
                summary="Successfully initialized SessionMaker",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            error = InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Failed initializing SessionMaker",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            )
            error.operation_schema.log(logger=self._logger, level=LogLevel.CRITICAL)

            raise error from e

    def _session_handler(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
    ) -> Generator[Session, None, None]:
        """Reusable function for managing database sessions."""
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.REPOSITORY,
            target=OperationTarget.DATABASE,
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        session = self._sessionmaker()
        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at, completed_at=None, duration=None
            ),
            summary="Successfully created new database session",
            request_context=request_context,
            authentication=authentication,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.DEBUG)
        try:
            yield session  # Provide session
            session.commit()  # Auto-commit on success
        except SQLAlchemyError as se:
            session.rollback()  # Rollback on error
            completed_at = datetime.now(tz=timezone.utc)
            error = DatabaseError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Database transaction failed and session rolled back successfully",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details=str(se),
            )
            error.operation_schema.log(logger=self._logger, level=LogLevel.ERROR)
            raise error from se
        except Exception as e:
            session.rollback()  # Rollback on error
            completed_at = datetime.now(tz=timezone.utc)
            error = InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Internal database error raised and session rolled back successfully",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                details=str(e),
            )
            error.operation_schema.log(logger=self._logger, level=LogLevel.ERROR)
            raise error from e
        finally:
            session.close()  # Ensure session closes
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
                summary="Database transaction succeeded and session closed",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)

    def inject(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
    ) -> Generator[Session, None, None]:
        """Returns a generator that yields a SQLAlchemy session for dependency injection."""
        return self._session_handler(
            operation_id=operation_id,
            request_context=request_context,
            authentication=authentication,
        )

    @contextmanager
    def get(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
    ) -> Generator[Session, None, None]:
        """Context manager for manual session handling. Supports `with SessionManager.get() as session:`"""
        yield from self._session_handler(
            operation_id=operation_id,
            request_context=request_context,
            authentication=authentication,
        )

    def dispose(
        self,
        operation_id: UUID,
    ) -> None:
        """Dispose of the sessionmaker and release any resources."""
        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.UTILITY,
            target=OperationTarget.DATABASE,
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DISPOSAL, details=None
        )

        if self._sessionmaker is not None:
            self._sessionmaker.close_all()

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=None,
            ),
            summary="Successfully disposed SessionManager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)


class DatabaseManager:
    def __init__(
        self,
        operation_id: UUID,
        metadata: MetaData,
        logger: DatabaseLogger,
        url: OptionalString = None,
        service_context: Optional[ServiceContext] = None,
    ):
        self._metadata = metadata
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self._operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.REPOSITORY,
            target=OperationTarget.DATABASE,
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION, details=None
        )

        initial_executed_at = datetime.now(tz=timezone.utc)

        # Create SQLAlchemy engine
        try:
            url = url or os.getenv("DB_URL")
            if url is None:
                raise ValueError(
                    "DB_URL environment variable must be set if url is not provided"
                )

            self._engine = create_engine(
                url=url, echo=False, pool_pre_ping=True, pool_recycle=3600
            )

            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=initial_executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - initial_executed_at).total_seconds(),
                ),
                summary="Successfully created SQLAlchemy Engine",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            error = InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=initial_executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - initial_executed_at).total_seconds(),
                ),
                operation_summary="Failed creating SQLAlchemy Engine",
                operation_action=operation_action,
                request_context=None,
                authentication=None,
                details=str(e),
            )
            error.operation_schema.log(logger=self._logger, level=LogLevel.CRITICAL)

            raise error from e

        metadata_executed_at = datetime.now(tz=timezone.utc)

        # Creating all table from metadata
        try:
            self._metadata.create_all(bind=self._engine)
            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=metadata_executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - initial_executed_at).total_seconds(),
                ),
                summary="Successfully created all tables defined in metadata",
                request_context=None,
                authentication=None,
                action=operation_action,
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            error = InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=initial_executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - initial_executed_at).total_seconds(),
                ),
                operation_summary="Failed creating all tables defined in metadata",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            )
            error.operation_schema.log(logger=self._logger, level=LogLevel.CRITICAL)
            raise error from e

        # Create session
        self._session = SessionManager(
            self._engine,
            logger=self._logger,
            operation_id=operation_id,
            service_context=service_context,
        )

        completed_at = datetime.now(tz=timezone.utc)
        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp(
                executed_at=initial_executed_at,
                completed_at=completed_at,
                duration=(completed_at - initial_executed_at).total_seconds(),
            ),
            summary="Successfully initialized DatabaseManager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    @property
    def metadata(self) -> MetaData:
        return self._metadata

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> SessionManager:
        return self._session

    def check_connection(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        authentication: Authentication,
    ) -> bool:
        """Check database connectivity by executing a simple query."""
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DATABASE_CONNECTION, details=None
        )
        executed_at = datetime.now(tz=timezone.utc)
        try:
            with self.session.get(
                operation_id=operation_id,
                request_context=request_context,
                authentication=authentication,
            ) as session:
                session.execute(text("SELECT 1"))
            completed_at = datetime.now(tz=timezone.utc)
            SuccessfulSystemOperationSchema(
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary="Database connectivity check successful",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                result=None,
            ).log(logger=self._logger, level=LogLevel.INFO)
            return True
        except Exception:
            return False

    def dispose(
        self,
        operation_id: UUID,
    ) -> None:
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DISPOSAL, details=None
        )
        # Dispose session
        if self._session is not None:
            self._session.dispose(operation_id)
        # Dispose engine
        if self._engine is not None:
            self._engine.dispose()

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=None,
            ),
            summary="Successfully disposed DatabaseManager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)
