from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timezone
from fastapi import Response
from typing import Optional
from uuid import UUID, uuid4
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    SystemOperationType,
    OperationOrigin,
    OperationLayer,
    OperationTarget,
)
from maleo.soma.schemas.operation.context import generate_operation_context
from maleo.soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
from maleo.soma.schemas.operation.system.action import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalUUID
from maleo.soma.utils.logging import MiddlewareLogger
from maleo.soma.utils.name import get_fully_qualified_name
from maleo.soma.utils.signature import sign


class ResponseBuilder:
    """ResponseBuilder class"""

    key = "response_builder"
    name = "ResponseBuilder"

    def __init__(
        self,
        logger: MiddlewareLogger,
        private_key: RsaKey,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
    ) -> None:
        self._logger = logger
        self._private_key = private_key
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
                    "key": "base_middleware",
                    "name": "Base Middleware",
                },
                "component": {"key": self.key, "name": self.name},
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

    def _add_signature_header(
        self,
        operation_id: UUID,
        request_id: UUID,
        method: str,
        url: str,
        requested_at: datetime,
        responded_at: datetime,
        process_time: float,
        response: Response,
    ) -> Response:
        message = (
            f"{str(operation_id)}|"
            f"{str(request_id)}"
            f"{method}|"
            f"{url}|"
            f"{requested_at.isoformat()}|"
            f"{responded_at.isoformat()}|"
            f"{str(process_time)}|"
        )

        try:
            signature = sign(message=message, key=self._private_key)
            response.headers["X-Signature"] = signature
        except Exception:
            pass

        return response

    def add_headers(
        self,
        operation_id: UUID,
        request_context: RequestContext,
        response: Response,
        responded_at: datetime,
        process_time: float,
    ) -> Response:
        """Add custom headers to response"""
        # Basic headers
        response.headers["X-Operation-Id"] = str(operation_id)
        response.headers["X-Request-Id"] = str(request_context.request_id)
        response.headers["X-Requested-At"] = request_context.requested_at.isoformat()
        response.headers["X-Responded-At"] = responded_at.isoformat()
        response.headers["X-Process-Time"] = str(process_time)

        response = self._add_signature_header(
            operation_id=operation_id,
            request_id=request_context.request_id,
            method=request_context.method,
            url=request_context.url,
            requested_at=request_context.requested_at,
            responded_at=responded_at,
            process_time=process_time,
            response=response,
        )

        return response
