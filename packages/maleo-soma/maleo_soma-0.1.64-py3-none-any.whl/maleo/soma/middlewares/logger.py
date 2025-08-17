from typing import Dict, Tuple, Type
from uuid import UUID
from maleo.soma.enums.logging import LogLevel
from maleo.soma.exceptions import Error
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.operation.context import OperationContextSchema
from maleo.soma.schemas.operation.request import (
    RequestOperationSchema,
    CreateFailedRequestOperationSchema,
    CreateSuccessfulRequestOperationSchema,
    DeleteFailedRequestOperationSchema,
    DeleteSuccessfulRequestOperationSchema,
    ReadFailedRequestOperationSchema,
    ReadSuccessfulRequestOperationSchema,
    UpdateFailedRequestOperationSchema,
    UpdateSuccessfulRequestOperationSchema,
)
from maleo.soma.schemas.operation.resource.action import (
    ResourceOperationActionSchema,
    CreateResourceOperationAction,
    DeleteResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
)
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.response import ResponseContext
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import MiddlewareLogger


class RequestOperationLogger:
    """Factory for creating operation log schemas."""

    # Schema mappings
    OPERATION_SCHEMAS: Dict[
        Tuple[Type[ResourceOperationActionSchema], bool], Type[RequestOperationSchema]
    ] = {
        (CreateResourceOperationAction, True): CreateSuccessfulRequestOperationSchema,
        (ReadResourceOperationAction, True): ReadSuccessfulRequestOperationSchema,
        (UpdateResourceOperationAction, True): UpdateSuccessfulRequestOperationSchema,
        (DeleteResourceOperationAction, True): DeleteSuccessfulRequestOperationSchema,
        (CreateResourceOperationAction, False): CreateFailedRequestOperationSchema,
        (ReadResourceOperationAction, False): ReadFailedRequestOperationSchema,
        (UpdateResourceOperationAction, False): UpdateFailedRequestOperationSchema,
        (DeleteResourceOperationAction, False): DeleteFailedRequestOperationSchema,
    }

    @classmethod
    def log(
        cls,
        logger: MiddlewareLogger,
        service_context: ServiceContext,
        operation_id: UUID,
        operation_context: OperationContextSchema,
        operation_timestamp: OperationTimestamp,
        request_context: RequestContext,
        authentication: Authentication,
        response_context: ResponseContext,
        resource_operation_action: ResourceOperationActionSchema,
        is_success: bool,
        error=None,
    ):
        """Create and log the appropriate operation schema."""

        schema_key = (type(resource_operation_action), is_success)
        schema_class = cls.OPERATION_SCHEMAS.get(schema_key)

        if schema_class is None:
            # Log unknown operation type or use a default
            logger.warning(f"Unknown operation type: {type(resource_operation_action)}")
            return

        # Build schema parameters
        schema_params = {
            "service_context": service_context,
            "id": operation_id,
            "context": operation_context,
            "timestamp": operation_timestamp,
            "request_context": request_context,
            "authentication": authentication,
            "action": resource_operation_action,
            "response_context": response_context,
        }

        # Add error for failed operations
        if not is_success and error:
            schema_params["error"] = error.schema if isinstance(error, Error) else None

        # Create and log
        log_level = LogLevel.INFO if is_success else LogLevel.ERROR
        schema_class(**schema_params).log(logger=logger, level=log_level)
