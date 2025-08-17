from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from typing import Optional
from uuid import uuid4, UUID
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationLayer,
    OperationOrigin,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.operation.context import generate_operation_context
from maleo.soma.schemas.operation.resource.action import (
    extract_resource_operation_action,
)
from maleo.soma.schemas.operation.system import SuccessfulSystemOperationSchema
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.response import InternalServerErrorResponseSchema
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalUUID
from maleo.soma.utils.logging import MiddlewareLogger
from maleo.soma.utils.name import get_fully_qualified_name


class StateMiddleware(BaseHTTPMiddleware):
    """Middleware for all request's state management"""

    key = "state_middleware"
    name = "StateMiddleware"

    def __init__(
        self,
        app: ASGIApp,
        logger: MiddlewareLogger,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        super().__init__(app, None)
        self._logger = logger
        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_id = operation_id if operation_id is not None else uuid4()

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.MIDDLEWARE,
            layer_details={
                "identifier": {
                    "key": self.key,
                    "name": self.name,
                }
            },
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION,
            details={
                "type": "class_initialization",
                "class_key": self.key,
                "class_name": self.name,
            },
        )

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=0,
            ),
            summary=f"Successfully initialized {self.name}",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            # Assign Operation Id
            operation_id = request.headers.get("X-Operation-Id", None)
            if not isinstance(operation_id, UUID):
                operation_id = uuid4()
            request.state.operation_id = operation_id

            # Assign Operation action
            resource_operation_action = extract_resource_operation_action(
                request, False
            )
            request.state.resource_operation_action = resource_operation_action

            # Assign Request Id
            request.state.request_id = uuid4()

            # Assign Requested at
            request.state.requested_at = datetime.now(tz=timezone.utc)

            # Assign Authentication
            authentication = Authentication.from_request(
                request=request, from_state=False
            )
            request.state.authentication = authentication

            # Call and return response
            return await call_next(request)
        except Exception as e:
            return JSONResponse(
                content=InternalServerErrorResponseSchema(other=str(e)).model_dump(
                    mode="json"
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def add_state_middleware(
    app: FastAPI,
    *,
    logger: MiddlewareLogger,
    service_context: Optional[ServiceContext] = None,
    operation_id: OptionalUUID = None,
) -> None:
    app.add_middleware(
        StateMiddleware,
        logger=logger,
        service_context=service_context,
        operation_id=operation_id,
    )
