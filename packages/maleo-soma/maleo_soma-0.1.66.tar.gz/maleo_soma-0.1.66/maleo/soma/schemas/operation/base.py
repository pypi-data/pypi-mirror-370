import traceback
from logging import Logger
from pydantic import BaseModel, Field
from typing import Generic, Optional
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import OperationType
from maleo.soma.mixins.general import GenericSuccess, SuccessT
from maleo.soma.mixins.operation import OperationIdentifier
from maleo.soma.mixins.operation import OperationSummary
from maleo.soma.schemas.authentication import OptionalAuthenticationMixin
from maleo.soma.schemas.error import AnyErrorMixin
from maleo.soma.schemas.operation.action import (
    OperationActionMixin,
    OperationActionSchemaT,
)
from maleo.soma.schemas.operation.context import OperationContextMixin
from maleo.soma.schemas.operation.timestamp import OperationTimestampMixin
from maleo.soma.schemas.request import OptionalRequestContextMixin
from maleo.soma.schemas.response import ResponseContext
from maleo.soma.schemas.service import ServiceContextMixin
from maleo.soma.types.base import (
    OptionalBoolean,
    StringToAnyDict,
    StringToStringDict,
    OptionalStringToStringDict,
)
from maleo.soma.utils.merger import merge_dicts


class OperationTypeMixin(BaseModel):
    type: OperationType = Field(..., description="Operation's type")


class BaseOperationSchema(
    OperationActionMixin[OperationActionSchemaT],
    OptionalAuthenticationMixin,
    OptionalRequestContextMixin,
    AnyErrorMixin,
    GenericSuccess[SuccessT],
    OperationSummary,
    OperationTimestampMixin,
    OperationContextMixin,
    OperationTypeMixin,
    OperationIdentifier,
    ServiceContextMixin,
    Generic[SuccessT, OperationActionSchemaT],
):
    @property
    def _response_context(self) -> Optional[ResponseContext]:
        _response_context = getattr(self, "response_context", None)
        if not isinstance(_response_context, ResponseContext):
            return None
        return _response_context

    @property
    def log_message(self) -> str:
        message = f"Operation {self.id} - {self.type} - "

        success_information = f"{'success' if self.success else 'failed'}"

        if self._response_context is not None:
            success_information += f" {self._response_context.status_code}"

        message += f"{success_information} - "

        if self.request_context is not None:
            message += (
                f"{self.request_context.method} {self.request_context.url} - "
                f"IP: {self.request_context.ip_address} - "
            )

        if self.authentication is None:
            authentication = "No Authentication"
        else:
            if not self.authentication.user.is_authenticated:
                authentication = "Unauthenticated"
            else:
                authentication = (
                    "Authenticated | "
                    f"Username: {self.authentication.user.display_name} | "
                    f"Email: {self.authentication.user.identity}"
                )

        message += f"{authentication} - "
        message += self.summary

        return message

    @property
    def labels(self) -> StringToStringDict:
        labels = {
            "service": self.service_context.key,
            "environment": self.service_context.environment,
            "operation_id": str(self.id),
            "operation_type": self.type,
            "success": "true" if self.success else "false",
        }

        if self.request_context is not None:
            labels["method"] = self.request_context.method
            labels["url"] = self.request_context.url
        if self._response_context is not None:
            labels["status_code"] = str(self._response_context.status_code)

        return labels

    def log_labels(
        self,
        *,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToStringDict:
        if override_labels is not None:
            return override_labels

        labels = self.labels
        if additional_labels is not None:
            for k, v in additional_labels.items():
                if k in labels.keys():
                    raise ValueError(
                        f"Key '{k}' already exist in labels, override the labels if necessary"
                    )
                labels[k] = v
            labels = merge_dicts(labels, additional_labels)
        return labels

    def log_extra(
        self,
        *,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToAnyDict:
        labels = self.log_labels(
            additional_labels=additional_labels, override_labels=override_labels
        )

        if override_extra is not None:
            extra = override_extra
        else:
            extra = {"json_fields": self.model_dump(mode="json"), "labels": labels}
            if additional_extra is not None:
                extra = merge_dicts(extra, additional_extra)

        return extra

    def log(
        self,
        logger: Logger,
        level: LogLevel,
        *,
        exc_info: OptionalBoolean = None,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ):
        try:
            message = self.log_message
            extra = self.log_extra(
                additional_extra=additional_extra,
                override_extra=override_extra,
                additional_labels=additional_labels,
                override_labels=override_labels,
            )
            logger.log(
                level,
                message,
                exc_info=exc_info,
                extra=extra,
            )
        except Exception:
            print("Failed logging operation schema:\n", traceback.format_exc())
