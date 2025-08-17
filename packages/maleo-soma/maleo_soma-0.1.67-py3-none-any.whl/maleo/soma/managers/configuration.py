from pathlib import Path
from typing import Optional
from maleo.soma.dtos.configurations import ConfigurationDTO
from maleo.soma.dtos.configurations.pubsub.publisher import (
    AdditionalTopicsConfigurationDTO,
)
from maleo.soma.dtos.settings import Settings
from maleo.soma.enums.secret import SecretFormat
from maleo.soma.managers.client.google.secret import GoogleSecretManager
from maleo.soma.types.base import OptionalUUID
from maleo.soma.utils.loaders.yaml import from_path, from_string


class ConfigurationManager:
    def __init__(
        self,
        settings: Settings,
        secret_manager: GoogleSecretManager,
        additional_topics_configurations: Optional[AdditionalTopicsConfigurationDTO],
        operation_id: OptionalUUID = None,
    ) -> None:
        use_local = settings.USE_LOCAL_CONFIGURATIONS
        config_path = settings.CONFIGURATIONS_PATH

        if use_local and config_path is not None and isinstance(config_path, str):
            config_path = Path(config_path)
            if config_path.exists() and config_path.is_file():
                data = from_path(config_path)
                self.configurations = ConfigurationDTO.model_validate(data)
                self.configurations.pubsub.publisher.topics.additional = (
                    additional_topics_configurations
                )
                return

        name = f"{settings.SERVICE_KEY}-configurations-{settings.ENVIRONMENT}"
        read_secret = secret_manager.read(
            SecretFormat.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.old.value)
        self.configurations = ConfigurationDTO.model_validate(data)
        self.configurations.pubsub.publisher.topics.additional = (
            additional_topics_configurations
        )
