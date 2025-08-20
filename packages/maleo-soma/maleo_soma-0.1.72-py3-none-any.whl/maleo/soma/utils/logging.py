import logging
import os
from datetime import datetime, timezone
from google.cloud.logging import Client
from google.cloud.logging.handlers import CloudLoggingHandler
from google.oauth2.service_account import Credentials
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.logging import LoggerType, LogLevel
from maleo.soma.enums.service import Service
from maleo.soma.schemas.logging import LogLabels
from maleo.soma.types.base import OptionalString, OptionalStringToStringDict
from maleo.soma.utils.loaders.credential.google import load
from maleo.soma.utils.merger import merge_dicts


class GoogleCloudLogging:
    def __init__(self, credentials_path: Optional[Union[Path, str]] = None) -> None:
        self._credentials = load(credentials_path=credentials_path)
        self._client = Client(credentials=self._credentials)
        self._client.setup_logging()

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @property
    def client(self) -> Client:
        return self._client

    def dispose(self) -> None:
        if self._client is not None:
            self._client.close

    def create_handler(
        self, name: str, labels: OptionalStringToStringDict = None
    ) -> CloudLoggingHandler:
        return CloudLoggingHandler(client=self._client, name=name, labels=labels)


class SimpleConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dir: str = Field(..., description="Log's directory")
    level: LogLevel = Field(LogLevel.INFO, description="Log's level")
    google_cloud_logging: Optional[GoogleCloudLogging] = Field(
        default_factory=GoogleCloudLogging, description="Google cloud logging"
    )


class BaseLogger(logging.Logger):
    def __init__(
        self,
        type: LoggerType,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        client_key: OptionalString = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        self._type = type  # Declare logger type

        # Ensure environment exists
        actual_environment = environment or os.getenv("ENVIRONMENT")
        if actual_environment is None:
            raise ValueError(
                "ENVIRONMENT environment variable must be set if 'environment' is set to None"
            )
        else:
            self._environment = Environment(actual_environment)

        # Ensure service_key exists
        actual_service_key = service_key or os.getenv("SERVICE_KEY")
        if actual_service_key is None:
            raise ValueError(
                "SERVICE_KEY environment variable must be set if 'service_key' is set to None"
            )
        else:
            self._service_key = Service(actual_service_key)

        self._client_key = client_key  # Declare client key

        # Ensure client_key is valid if logger type is a client
        if self._type == LoggerType.CLIENT and self._client_key is None:
            raise ValueError(
                "'client_key' parameter must be provided if 'logger_type' is 'client'"
            )

        # Define logger name
        base_name = f"{self._environment} - {self._service_key} - {self._type}"
        if self._type == LoggerType.CLIENT:
            self._name = f"{base_name} - {self._client_key}"
        else:
            self._name = base_name

        # Define log labels
        self._labels = LogLabels(
            logger_type=self._type,
            service_environment=self._environment,
            service_key=self._service_key,
            client_key=client_key,
        )

        super().__init__(self._name, level)  # Init the superclass's logger

        # Clear existing handlers to prevent duplicates
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.addHandler(console_handler)

        # Google Cloud Logging handler (If enabled)
        if google_cloud_logging is not None:
            final_labels = self._labels.model_dump(mode="json", exclude_none=True)
            if labels is not None:
                final_labels = merge_dicts(final_labels, labels)
            cloud_logging_handler = google_cloud_logging.create_handler(
                name=self._name.replace(" ", ""),
                labels=final_labels,
            )
            self.addHandler(cloud_logging_handler)
        else:
            self.warning(
                "Cloud logging is not configured. Will not add cloud logging handler"
            )

        # Define aggregate log directory
        if aggregate_file_name is not None:
            if not aggregate_file_name.endswith(".log"):
                aggregate_file_name += ".log"
            log_filename = os.path.join(self._log_dir, "aggregate", aggregate_file_name)

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

        if inidividual_log:
            # Define log directory
            if self._type == LoggerType.CLIENT:
                log_dir = f"{self._type}/{self._client_key}"
            else:
                log_dir = f"{self._type}"
            self._log_dir = os.path.join(dir, log_dir)
            os.makedirs(self._log_dir, exist_ok=True)

            # Generate timestamped filename
            log_filename = os.path.join(
                self._log_dir,
                f"{datetime.now(tz=timezone.utc).isoformat(timespec="seconds")}.log",
            )

            # File handler
            file_handler = logging.FileHandler(log_filename, mode="a")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

    @property
    def type(self) -> str:
        return self._type

    @property
    def location(self) -> str:
        return self._log_dir

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def service(self) -> str:
        return self._service_key

    @property
    def client(self) -> OptionalString:
        return self._client_key

    @property
    def identity(self) -> str:
        return self._name

    @property
    def labels(self) -> LogLabels:
        return self._labels

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()


class ApplicationLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.APPLICATION,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class CacheLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.CACHE,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class ClientLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        client_key: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.CLIENT,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=client_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class ControllerLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            dir=dir,
            type=LoggerType.CONTROLLER,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class DatabaseLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level=LogLevel.INFO,
        google_cloud_logging=None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.DATABASE,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class MiddlewareLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level=LogLevel.INFO,
        google_cloud_logging=None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.MIDDLEWARE,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class RepositoryLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.REPOSITORY,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )


class ServiceLogger(BaseLogger):
    def __init__(
        self,
        dir: str,
        environment: Optional[Environment] = None,
        service_key: Optional[Service] = None,
        level: LogLevel = LogLevel.INFO,
        google_cloud_logging: Optional[GoogleCloudLogging] = None,
        labels: OptionalStringToStringDict = None,
        aggregate_file_name: OptionalString = None,
        inidividual_log: bool = True,
    ):
        super().__init__(
            type=LoggerType.SERVICE,
            dir=dir,
            environment=environment,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging,
            labels=labels,
            aggregate_file_name=aggregate_file_name,
            inidividual_log=inidividual_log,
        )
