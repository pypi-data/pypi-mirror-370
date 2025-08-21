import os
from datetime import datetime, timedelta, timezone
from google.cloud.storage import Bucket, Client
from google.oauth2.service_account import Credentials
from pathlib import Path
from redis.asyncio.client import Redis
from typing import Optional, Union
from uuid import uuid4
from maleo.soma.enums.expiration import Expiration
from maleo.soma.enums.logging import LogLevel
from maleo.soma.enums.operation import (
    OperationLayer,
    SystemOperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
)
from maleo.soma.exceptions import NotFound, InternalServerError
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.data import DataPair
from maleo.soma.schemas.data.google.storage import StorageDataSchema
from maleo.soma.schemas.operation.system import (
    SuccessfulSystemOperationSchema,
)
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
from maleo.soma.schemas.operation.system import SystemOperationActionSchema
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.resource import Resource
from maleo.soma.schemas.resource.identifier import ResourceIdentifier
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalString, OptionalUUID
from maleo.soma.utils.logging import SimpleConfig
from .base import GoogleClientManager


class GoogleCloudStorage(GoogleClientManager):
    def __init__(
        self,
        log_config: SimpleConfig,
        service_context: Optional[ServiceContext] = None,
        operation_id: OptionalUUID = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
        bucket_name: OptionalString = None,
        redis: Optional[Redis] = None,
    ) -> None:
        executed_at = datetime.now(tz=timezone.utc)
        key = "google-cloud-storage"
        name = "GoogleCloudStorage"
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
        self._client = Client(credentials=self._credentials)

        try:
            self._bucket_name = None
            if bucket_name is not None:
                self._bucket_name = bucket_name
            else:
                env_bucket_name = os.getenv("GCS_BUCKET_NAME", None)
                if env_bucket_name is not None:
                    self._bucket_name = env_bucket_name

            if self._bucket_name is None:
                self._client.close()
                raise ValueError(
                    "Unable to determine 'bucket_name' either from argument or environment variable"
                )

            self._bucket = self._client.lookup_bucket(bucket_name=self._bucket_name)
            if self._bucket is None:
                self._client.close()
                raise ValueError(f"Bucket '{self._bucket_name}' does not exist.")

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
                operation_summary=f"Unexpected error raised while initializing {name} client manager",
                request_context=None,
                authentication=None,
                operation_action=operation_action,
                details=str(e),
            ) from e

        self._redis = redis
        self._root_location = self._service_context.key

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
    def bucket_name(self) -> str:
        if self._bucket_name is None:
            raise ValueError("Bucket name has not been initialized.")
        return self._bucket_name

    @property
    def bucket(self) -> Bucket:
        if self._bucket is None:
            raise ValueError("Bucket has not been initialized.")
        return self._bucket

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            raise ValueError("Redis has not been initialized.")
        return self._redis

    def dispose(
        self,
        operation_id: OptionalUUID = None,
    ) -> None:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = SystemOperationActionSchema(
            type=SystemOperationType.DISPOSAL, details=None
        )

        if self._client is not None:
            self._client.close()

        SuccessfulSystemOperationSchema(
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp(
                executed_at=datetime.now(tz=timezone.utc),
                completed_at=None,
                duration=None,
            ),
            summary=f"Successfully disposed {self.name} client manager",
            request_context=None,
            authentication=None,
            action=operation_action,
            result=None,
        ).log(logger=self._logger, level=LogLevel.INFO)

    async def upload(
        self,
        content: bytes,
        location: str,
        content_type: OptionalString = None,
        root_location_override: OptionalString = None,
        make_public: bool = False,
        set_in_redis: bool = True,
        expiration: Expiration = Expiration.EXP_15MN,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> CreateSingleResourceOperationResult[StorageDataSchema, None]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = CreateResourceOperationAction(
            type=ResourceOperationType.CREATE,
            create_type=ResourceOperationCreateType.NEW,
        )

        resource = Resource(
            identifiers=[
                ResourceIdentifier(
                    key="object_storage",
                    name="ObjectStorage",
                    url_slug="object-storage",
                )
            ],
            details={"object_location": location},
        )

        executed_at = datetime.now(tz=timezone.utc)

        try:
            if root_location_override is None or (
                isinstance(root_location_override, str)
                and len(root_location_override) <= 0
            ):
                blob_name = f"{self._root_location}/{location}"
            else:
                blob_name = f"{root_location_override}/{location}"

            blob = self.bucket.blob(blob_name=blob_name)
            blob.upload_from_string(content, content_type=content_type or "text/plain")

            if make_public:
                blob.make_public()
                url = blob.public_url
            else:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(seconds=int(expiration)),
                    method="GET",
                )

            if set_in_redis:
                ex = None if make_public else int(expiration)
                await self.redis.set(
                    f"{self.service_context.key}:{self.key}:{blob_name}",
                    url,
                    ex=ex,
                )

            completed_at = datetime.now(tz=timezone.utc)
            data = DataPair[None, StorageDataSchema](
                old=None,
                new=StorageDataSchema(url=url),
            )
            result = CreateSingleResourceOperationResult[StorageDataSchema, None](
                data=data, metadata=None, other=None
            )
            CreateSingleResourceOperationSchema[StorageDataSchema, None](
                service_context=self._service_context,
                id=operation_id,
                context=self._operation_context,
                timestamp=OperationTimestamp(
                    executed_at=executed_at,
                    completed_at=completed_at,
                    duration=(completed_at - executed_at).total_seconds(),
                ),
                summary=f"Successfully uploaded object to '{location}'",
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
                operation_summary="Unexpected error raised while uploading object",
                request_context=request_context,
                authentication=authentication,
                operation_action=operation_action,
                resource=resource,
                details=str(e),
            ) from e

    async def generate_signed_url(
        self,
        location: str,
        root_location_override: OptionalString = None,
        search_in_redis: bool = True,
        expiration: Expiration = Expiration.EXP_15MN,
        operation_id: OptionalUUID = None,
        request_context: Optional[RequestContext] = None,
        authentication: Optional[Authentication] = None,
    ) -> ReadSingleResourceOperationResult[StorageDataSchema, None]:
        operation_id = operation_id if operation_id is not None else uuid4()
        operation_action = ReadResourceOperationAction()

        resource = Resource(
            identifiers=[
                ResourceIdentifier(
                    key="object_storage",
                    name="ObjectStorage",
                    url_slug="object-storage",
                )
            ],
            details={"object_location": location},
        )

        executed_at = datetime.now(tz=timezone.utc)

        if root_location_override is None or (
            isinstance(root_location_override, str) and len(root_location_override) <= 0
        ):
            blob_name = f"{self._root_location}/{location}"
        else:
            blob_name = f"{root_location_override}/{location}"

        if search_in_redis:
            url = await self.redis.get(
                f"{self.service_context.key}:{self.key}:{blob_name}"
            )
            if url is not None:
                completed_at = datetime.now(tz=timezone.utc)
                data = DataPair[StorageDataSchema, None](
                    old=StorageDataSchema(url=url),
                    new=None,
                )
                result = ReadSingleResourceOperationResult[StorageDataSchema, None](
                    data=data, metadata=None, other=None
                )
                ReadSingleResourceOperationSchema[StorageDataSchema, None](
                    service_context=self._service_context,
                    id=operation_id,
                    summary=f"Successfully generated presigned url for file '{location}'",
                    timestamp=OperationTimestamp(
                        executed_at=executed_at,
                        completed_at=completed_at,
                        duration=(completed_at - executed_at).total_seconds(),
                    ),
                    action=operation_action,
                    context=self._operation_context,
                    request_context=request_context,
                    authentication=authentication,
                    resource=resource,
                    result=result,
                ).log(self._logger, level=LogLevel.INFO)
                return result

        blob = self.bucket.blob(blob_name=blob_name)
        if not blob.exists():
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
                operation_summary=f"Object '{location}' not found",
                request_context=request_context,
                authentication=authentication,
                resource=resource,
                operation_action=operation_action,
            )

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration.value),
            method="GET",
        )

        if search_in_redis:
            await self.redis.set(
                f"{self.service_context.key}:{blob_name}", url, ex=expiration.value
            )

        completed_at = datetime.now(tz=timezone.utc)
        data = DataPair[StorageDataSchema, None](
            old=StorageDataSchema(url=url),
            new=None,
        )
        result = ReadSingleResourceOperationResult[StorageDataSchema, None](
            data=data, metadata=None, other=None
        )
        ReadSingleResourceOperationSchema[StorageDataSchema, None](
            service_context=self._service_context,
            id=operation_id,
            context=self._operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary=f"Successfully generated presigned url for object '{location}'",
            request_context=request_context,
            authentication=authentication,
            action=operation_action,
            resource=resource,
            result=result,
        ).log(self._logger, level=LogLevel.INFO)
        return result
