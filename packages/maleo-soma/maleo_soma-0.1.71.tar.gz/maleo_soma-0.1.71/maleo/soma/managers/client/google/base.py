from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Optional, Union
from maleo.soma.enums.operation import OperationTarget
from maleo.soma.managers.client.base import ClientManager
from maleo.soma.schemas.operation.context import OperationTargetSchema
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.loaders.credential.google import load
from maleo.soma.utils.logging import SimpleConfig


class GoogleClientManager(ClientManager):
    def __init__(
        self,
        key: str,
        name: str,
        log_config: SimpleConfig,
        service_context: Optional[ServiceContext] = None,
        credentials: Optional[Credentials] = None,
        credentials_path: Optional[Union[Path, str]] = None,
    ) -> None:
        super().__init__(key, name, log_config, service_context)
        if (credentials is not None and credentials_path is not None) or (
            credentials is None and credentials_path is None
        ):
            raise ValueError(
                "Only either 'credentials' or 'credentials_path' can be passed as parameter"
            )

        if credentials is not None:
            self._credentials = credentials
        else:
            self._credentials = load(credentials_path)

        self._project_id = self._credentials.project_id

        self._operation_target = OperationTargetSchema(
            type=OperationTarget.INTERNAL, details=None
        )

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @property
    def project_id(self) -> str:
        if self._project_id is None:
            raise ValueError("Project ID has not been initialized.")
        return self._project_id
