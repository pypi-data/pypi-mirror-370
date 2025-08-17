from Crypto.PublicKey.RSA import RsaKey
from google.oauth2.service_account import Credentials
from maleo.soma.dtos.credential import CredentialDTO, MaleoCredentialDTO
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.secret import SecretFormat
from maleo.soma.managers.client.google.secret import GoogleSecretManager
from maleo.soma.schemas.token import CredentialPayload
from maleo.soma.types.base import OptionalString, OptionalUUID
from maleo.soma.utils.loaders.yaml import from_string
from maleo.soma.utils.token import encode


class CredentialManager:
    def __init__(
        self,
        environment: Environment,
        private_key: RsaKey,
        secret_manager: GoogleSecretManager,
        operation_id: OptionalUUID = None,
    ) -> None:
        self._private_key = private_key
        self._secret_manager = secret_manager

        name = f"maleo-internal-credentials-{environment}"
        read_secret = secret_manager.read(
            SecretFormat.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.old.value)
        self.maleo_credentials = MaleoCredentialDTO.model_validate(data)

    def assign_google_credentials(self, google_credentials: Credentials) -> None:
        self.google_credentials = google_credentials

    @property
    def credentials(self) -> CredentialDTO:
        if not hasattr(self, "google_credentials") or not isinstance(
            self.google_credentials, Credentials
        ):
            raise ValueError("Google credential not initialized")
        if not hasattr(self, "maleo_credentials") or not isinstance(
            self.maleo_credentials, MaleoCredentialDTO
        ):
            raise ValueError("Maleo credential not initialized")
        return CredentialDTO(
            google=self.google_credentials, maleo=self.maleo_credentials
        )

    @property
    def token(self) -> OptionalString:
        credential = CredentialPayload(
            iss=None,
            sub=str(self.maleo_credentials.id),
            sr="administrator",
            u_i=self.maleo_credentials.id,
            u_uu=self.maleo_credentials.uuid,
            u_u=self.maleo_credentials.username,
            u_e=self.maleo_credentials.email,
            u_ut="service",
            o_i=None,
            o_uu=None,
            o_k=None,
            o_ot=None,
            uor=None,
        )
        try:
            return encode(credential=credential, key=self._private_key)
        except Exception:
            return None
