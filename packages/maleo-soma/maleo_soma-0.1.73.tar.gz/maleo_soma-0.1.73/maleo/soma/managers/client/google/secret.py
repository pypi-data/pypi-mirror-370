from datetime import datetime, timezone
from google.api_core.exceptions import NotFound as GoogleNotFound
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Any, Optional, Union, overload
from uuid import uuid4
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationLayer,
    SystemOperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
)
from maleo.soma.enums.secret import SecretFormat
from maleo.soma.exceptions import NotFound, InternalServerError
from maleo.soma.mappings.secret import FORMAT_TYPE_MAPPING
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.data import DataPair
from maleo.soma.schemas.operation.system import SystemOperationActionSchema
from maleo.soma.schemas.operation.context import (
    OperationContextSchema,
    OperationLayerSchema,
)
from maleo.soma.schemas.operation.resource import (
    CreateSingleResourceOperationSchema,
    ReadSingleResourceOperationSchema,
)
from maleo.soma.schemas.operation.resource.action import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
)
from maleo.soma.schemas.operation.resource.result import (
    CreateSingleResourceOperationResult,
    ReadSingleResourceOperationResult,
)
from maleo.soma.schemas.operation.system import SuccessfulSystemOperationSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.data.google.secret import SecretDataSchema
from maleo.soma.schemas.resource import Resource
from maleo.soma.schemas.resource.identifier import ResourceIdentifier
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalUUID
from maleo.soma.types.literals.secret import (
    SecretFormatLiteral,
    BytesSecretFormatLiteral,
    StringSecretFormatLiteral,
)
from maleo.soma.utils.logging import SimpleConfig
from .base import GoogleClientManager


class GoogleSecretManager(GoogleClientManager):
    def __init__(
        self,
        log_config: SimpleConfig,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
    ) -> None:
        executed_at = datetime.now(tz=timezone.utc)
        key = "google-secret-manager"
        name = "GoogleSecretManager"
        operation_id = operation_id if operation_id is not None else uuid4()
        super().__init__(
            key,
            name,
            log_config,
            service_context,
            credentials,
            credentials_path,
        )
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.INITIALIZATION, details=None
        )
        self._operation_context = OperationContextSchema(
            origin=self._operation_origin,
            layer=OperationLayerSchema(type=OperationLayer.SERVICE, details=None),
            target=self._operation_target,
        )
        self._client = secretmanager.SecretManagerServiceClient(
            credentials=self._credentials
        )
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
            summary=f"Successfully initialized {name} client manager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        return self._client

    @overload
    def create(
        self,
        name: str,
        value: bytes,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> CreateSingleResourceOperationResult[SecretDataSchema[bytes], None]: ...
    @overload
    def create(
        self,
        name: str,
        value: str,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> CreateSingleResourceOperationResult[SecretDataSchema[str], None]: ...
    def create(
        self,
        name: str,
        value: Union[bytes, str],
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> CreateSingleResourceOperationResult[SecretDataSchema[Any], None]:
        if not isinstance(value, (bytes, str)):
            raise TypeError("Value type can only either be 'bytes' or 'str'")
        value_type = type(value)

        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = CreateResourceOperationAction(
            type=ResourceOperationType.CREATE,
            create_type=ResourceOperationCreateType.NEW,
        )

        resource = Resource(
            identifiers=[
                ResourceIdentifier(key="secret", name="Secret", url_slug="secret")
            ],
            details={"secret_name": name},
        )

        executed_at = datetime.now(tz=timezone.utc)

        parent = f"projects/{self._project_id}"
        secret_path = f"{parent}/secrets/{name}"
        # Check if the secret already exists
        try:
            request = secretmanager.GetSecretRequest(name=secret_path)
            self._client.get_secret(request=request)
        except GoogleNotFound:
            # Secret does not exist, create it first
            try:
                secret = secretmanager.Secret(name=name, replication={"automatic": {}})
                request = secretmanager.CreateSecretRequest(
                    parent=parent, secret_id=name, secret=secret
                )
                self._client.create_secret(request=request)
            except Exception as e:
                completed_at = datetime.now(tz=timezone.utc)
                raise InternalServerError(
                    service_context=self._service_context,
                    operation_id=operation_id,
                    operation_context=self._operation_context,
                    operation_timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    operation_summary="Unexpected error raised while creating new secret",
                    request_context=request_context,
                    authentication=authentication,
                    operation_action=operation_action,
                    resource=resource,
                    details=str(e),
                ) from e

        # Add a new secret version
        try:
            value = value.encode() if isinstance(value, str) else value
            payload = secretmanager.SecretPayload(data=value)
            request = secretmanager.AddSecretVersionRequest(
                parent=secret_path, payload=payload
            )
            self._client.add_secret_version(request=request)
            completed_at = datetime.now(tz=timezone.utc)
            data = DataPair[None, SecretDataSchema[value_type]](
                old=None,
                new=SecretDataSchema[value_type](
                    name=name, version="latest", value=value
                ),
            )
            result = CreateSingleResourceOperationResult[
                SecretDataSchema[value_type], None
            ](data=data, metadata=None, other=None)
            CreateSingleResourceOperationSchema[SecretDataSchema[value_type], None](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully added new secret '{name}' version",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=resource,
                result=result,
            ).log(self._logger, level=LogLevel.INFO)
            return result
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary="Unexpected error raised while adding new secret version",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=str(e),
            ) from e

    @overload
    def read(
        self,
        format: BytesSecretFormatLiteral,
        name: str,
        version: str = "latest",
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> ReadSingleResourceOperationResult[SecretDataSchema[bytes], None]: ...

    @overload
    def read(
        self,
        format: StringSecretFormatLiteral,
        name: str,
        version: str = "latest",
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> ReadSingleResourceOperationResult[SecretDataSchema[str], None]: ...

    def read(
        self,
        format: SecretFormatLiteral,
        name: str,
        version: str = "latest",
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> ReadSingleResourceOperationResult[SecretDataSchema[Any], None]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = ReadResourceOperationAction()

        value_type = FORMAT_TYPE_MAPPING.get(format, None)
        if value_type is None:
            raise ValueError(
                f"Unable to determine secret value type for given format: '{format}'"
            )

        executed_at = datetime.now(tz=timezone.utc)

        resource = Resource(
            identifiers=[
                ResourceIdentifier(key="secret", name="Secret", url_slug="secret")
            ],
            details={"secret_name": name},
        )

        # Check if secret exists
        secret_name = f"projects/{self._project_id}/secrets/{name}"
        try:
            request = secretmanager.GetSecretRequest(name=secret_name)
            self._client.get_secret(request=request)
        except GoogleNotFound as gnf:
            completed_at = datetime.now(tz=timezone.utc)
            raise NotFound(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Secret '{secret_name}' not found",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=gnf.reason,
            ) from gnf
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Exception raised while ensuring secret '{secret_name}' exists",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=str(e),
            ) from e

        # Check if secret's version exists
        secret_version_name = f"{secret_name}/versions/{version}"
        try:
            request = secretmanager.GetSecretVersionRequest(name=secret_version_name)
            self._client.get_secret_version(request=request)
        except GoogleNotFound as gnf:
            completed_at = datetime.now(tz=timezone.utc)
            raise NotFound(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Secret's version '{secret_version_name}' not found",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=gnf.reason,
            ) from gnf
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Exception raised while ensuring secret's version '{secret_version_name}' exists",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=str(e),
            ) from e

        try:
            request = secretmanager.AccessSecretVersionRequest(name=secret_version_name)
            response = self._client.access_secret_version(request=request)
            completed_at = datetime.now(tz=timezone.utc)

            if format is SecretFormat.BYTES:
                value = response.payload.data
            elif format is SecretFormat.STRING:
                value = response.payload.data.decode()

            data = DataPair[SecretDataSchema[value_type], None](
                old=SecretDataSchema[value_type](
                    name=name, version=version, value=value
                ),
                new=None,
            )
            result = ReadSingleResourceOperationResult[
                SecretDataSchema[value_type], None
            ](data=data, metadata=None, other=None)
            ReadSingleResourceOperationSchema[SecretDataSchema[value_type], None](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully retrieved secret '{name}' with version '{version}'",
                request_context=request_context,
                authentication=authentication,
                action=operation_action,
                resource=resource,
                result=result,
            ).log(self._logger, level=LogLevel.INFO)
            return result
        except Exception as e:
            completed_at = datetime.now(tz=timezone.utc)
            raise InternalServerError(
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                operation_summary=f"Exception raised while accessing secret's version '{secret_version_name}'",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=str(e),
            ) from e
