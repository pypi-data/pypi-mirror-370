from io import BytesIO
import traceback
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp
from typing import Optional
from uuid import uuid4
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationOrigin,
    OperationLayer,
    OperationTarget,
    SystemOperationType,
)
from maleo.soma.exceptions import TooManyRequests, InternalServerError
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.operation.context import generate_operation_context
from maleo.soma.schemas.operation.resource.action import (
    extract_resource_operation_action,
)
from maleo.soma.schemas.operation.system import SuccessfulSystemOperationSchema
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.response import (
    ResponseContext,
    TooManyRequestsResponseSchema,
    InternalServerErrorResponseSchema,
)
from maleo.soma.types.base import OptionalUUID
from maleo.soma.utils.logging import MiddlewareLogger
from maleo.soma.utils.name import get_fully_qualified_name
from .logger import RequestOperationLogger
from .rate_limit import RateLimiter
from .response_builder import ResponseBuilder


class BaseMiddleware(BaseHTTPMiddleware):
    """Base Middleware for Maleo"""

    key = "base_middleware"
    name = "Base Middleware"

    def __init__(
        self,
        app: ASGIApp,
        logger: MiddlewareLogger,
        private_key: RsaKey,
        rate_limiter: RateLimiter,
        response_builder: ResponseBuilder,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        super().__init__(app, None)
        self._logger = logger
        self._private_key = private_key

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        operation_id = operation_id if operation_id is not None else uuid4()

        self.rate_limiter = rate_limiter

        self._response_builder = response_builder

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
        # Get all necessary states
        try:
            # Get Operation Id
            operation_id = request.state.operation_id

            # Get Request Context
            request_context = RequestContext.from_request(request=request)

            # Get Authentication
            authentication = Authentication.from_request(
                request=request, from_state=True
            )

            # Get Operation action
            resource_operation_action = extract_resource_operation_action(
                request=request
            )

        except Exception as e:
            print("Unable to retrieve request's state:\n", traceback.format_exc())
            response = JSONResponse(
                content=InternalServerErrorResponseSchema(other=str(e)).model_dump(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return response

        operation_context = generate_operation_context(
            origin=OperationOrigin.SERVICE,
            layer=OperationLayer.MIDDLEWARE,
            layer_details={"type": "base"},
            target=OperationTarget.INTERNAL,
            target_details={"fully_qualified_name": get_fully_qualified_name()},
        )

        executed_at = datetime.now(tz=timezone.utc)
        error = None

        try:
            user_id = (
                authentication.credentials.token.payload.u_i
                if authentication.credentials.token is not None
                else None
            )
            organization_id = (
                authentication.credentials.token.payload.o_i
                if authentication.credentials.token is not None
                else None
            )
            is_rate_limited = await self.rate_limiter.is_rate_limited(
                ip_address=request_context.ip_address,
                user_id=user_id,
                organization_id=organization_id,
            )
            if is_rate_limited:
                completed_at = datetime.now(tz=timezone.utc)
                raise TooManyRequests(
                    service_context=self._service_context,
                    operation_id=operation_id,
                    operation_context=operation_context,
                    operation_timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    operation_summary="Too many requests",
                    request_context=request_context,
                    authentication=authentication,
                    operation_action=resource_operation_action,
                )
            response = await call_next(request)
        except TooManyRequests as tmr:
            error = tmr
            response = JSONResponse(
                content=TooManyRequestsResponseSchema().model_dump(),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except Exception as e:
            print("Failed processing request:\n", traceback.format_exc())
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
                operation_summary="Failed processing request",
                operation_action=resource_operation_action,
                request_context=request_context,
                authentication=authentication,
                details=str(e),
            )
            response = JSONResponse(
                content=InternalServerErrorResponseSchema(other=str(e)).model_dump(
                    mode="json"
                ),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        completed_at = datetime.now(tz=timezone.utc)

        duration = (completed_at - executed_at).total_seconds()
        response = self._response_builder.add_headers(
            operation_id=operation_id,
            request_context=request_context,
            response=response,
            responded_at=completed_at,
            process_time=duration,
        )

        operation_timestamp = OperationTimestamp(
            executed_at=executed_at, completed_at=completed_at, duration=duration
        )

        if hasattr(response, "body_iterator"):
            # Use BytesIO to efficiently collect the body
            body_buffer = BytesIO()
            async for chunk in response.body_iterator:  # type: ignore
                # Handle both string and bytes chunks
                if isinstance(chunk, str):
                    body_buffer.write(chunk.encode("utf-8"))
                elif isinstance(chunk, (bytes, memoryview)):
                    body_buffer.write(chunk)
                else:
                    # Handle any other types by converting to string first
                    body_buffer.write(str(chunk).encode("utf-8"))

            response_body = body_buffer.getvalue()

            response = StreamingResponse(
                iter([response_body]),
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.headers.get("content-type"),
            )
        else:
            try:
                response_body = getattr(response, "body", b"")
            except Exception:
                print(
                    "Failed retrieving response's body attribute:\n",
                    traceback.format_exc(),
                )
                response_body = b""

        response_context = ResponseContext(
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers.items(),
            body=response_body,
        )

        if 200 <= response.status_code < 300:
            RequestOperationLogger.log(
                logger=self._logger,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=operation_timestamp,
                request_context=request_context,
                authentication=authentication,
                response_context=response_context,
                resource_operation_action=resource_operation_action,
                is_success=True,
            )
        elif response.status_code >= 400:
            RequestOperationLogger.log(
                logger=self._logger,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=operation_timestamp,
                request_context=request_context,
                authentication=authentication,
                response_context=response_context,
                resource_operation_action=resource_operation_action,
                is_success=False,
                error=error,
            )

        # Call and return response
        return response


def add_base_middleware(
    app: FastAPI,
    *,
    logger: MiddlewareLogger,
    private_key: RsaKey,
    rate_limiter: RateLimiter,
    response_builder: ResponseBuilder,
    service_context: Optional[ServiceContext] = None,
    operation_id: OptionalUUID = None,
) -> None:
    """
    Add Base middleware to the FastAPI application.

    Args:
        app:FastAPI application instance
        keys:RSA keys for signing and token generation
        logger:Middleware logger instance
        maleo_soma:Client manager for soma services
        allow_origins:CORS allowed origins
        allow_methods:CORS allowed methods
        allow_headers:CORS allowed headers
        allow_credentials:CORS allow credentials flag
        limit:Request count limit per window
        window:Time window for rate limiting (seconds)
        cleanup_interval:Cleanup interval for old IP data (seconds)
        ip_timeout:IP timeout after last activity (seconds)

    Example:
        ```python
        add_base_middleware(
            app=app,
            keys=rsa_keys,
            logger=middleware_logger,
            maleo_soma=client_manager,
            limit=10,
            window=1,
            cleanup_interval=60,
            ip_timeout=300
        )
        ```
    """
    app.add_middleware(
        BaseMiddleware,
        logger=logger,
        private_key=private_key,
        rate_limiter=rate_limiter,
        response_builder=response_builder,
        service_context=service_context,
        operation_id=operation_id,
    )
