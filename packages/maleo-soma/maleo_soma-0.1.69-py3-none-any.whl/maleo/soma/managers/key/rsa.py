from maleo.soma.dtos.settings import Settings
from maleo.soma.enums.secret import SecretFormat
from maleo.soma.managers.client.google.secret import GoogleSecretManager
from maleo.soma.schemas.key.rsa import Complete
from maleo.soma.types.base import OptionalUUID


class RSAKeyManager:
    def __init__(
        self,
        settings: Settings,
        secret_manager: GoogleSecretManager,
        operation_id: OptionalUUID = None,
    ) -> None:
        if settings.KEY_PASSWORD is not None:
            password = settings.KEY_PASSWORD
        else:
            read_key_password = secret_manager.read(
                SecretFormat.STRING,
                name="maleo-key-password",
                operation_id=operation_id,
            )
            password = read_key_password.data.old.value

        if settings.PRIVATE_KEY is not None:
            private = settings.PRIVATE_KEY
        else:
            read_private_key = secret_manager.read(
                SecretFormat.STRING, name="maleo-private-key", operation_id=operation_id
            )
            private = read_private_key.data.old.value

        if settings.PUBLIC_KEY is not None:
            public = settings.PUBLIC_KEY
        else:
            read_public_key = secret_manager.read(
                SecretFormat.STRING, name="maleo-public-key", operation_id=operation_id
            )
            public = read_public_key.data.old.value

        self.keys = Complete(password=password, private=private, public=public)
