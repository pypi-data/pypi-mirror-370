import enum
from typing import Optional

from httpx import AsyncClient, ReadTimeout
from kink import di
from starlette import status

from appodus_utils import Utils
from appodus_utils.exception.exceptions import InternalServerException

from appodus_utils.sdk.appodus_sdk.services.chatbot_client import ChatbotClient
from appodus_utils.sdk.appodus_sdk.services.contract_client import ContractClient
from appodus_utils.sdk.appodus_sdk.services.document_client import DocumentClient
from appodus_utils.sdk.appodus_sdk.services.message_client import MessageClient
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class ApiVersion(str, enum.Enum):
    V1 = "v1"


class AppodusClient:
    """
    This is a utility class that abstracts the various Appodus utility services:
    [document_manager, contract_manager, communication_manager]
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_version: ApiVersion = ApiVersion.V1,
        service_url: Optional[str] = None,
        http_client: Optional[AsyncClient] = None,
    ) -> None:
        """
        :param client_id: Optional override for APPODUS_CLIENT_ID. OAuth client ID for authentication.
        :param client_secret: Optional override for APPODUS_CLIENT_SECRET. OAuth client secret
        :param api_version: API version to use (e.g., ApiVersion.V1)
        :param service_url: Optional override for APPODUS_SERVICES_URL
        :param http_client: Optional injected AsyncClient for testing
        """
        self._appodus_service_url = service_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_version = api_version
        self._http_client = http_client or di[AsyncClient]

        self.client_utils: Optional[AppodusClientUtils] = None

        self._contract_client: Optional[ContractClient] = None
        self._document_client: Optional[DocumentClient] = None
        self._chatbot_client: Optional[ChatbotClient] = None
        self._message_client: Optional[MessageClient] = None

    def init(self) -> 'AppodusClient':
        """Initializes Appodus service clients and checks connectivity."""
        try:
            self._load_config()
            self._create_client_utils()
            self._init_clients()
            # await self._check_service_health()
        except Exception as e:
            raise InternalServerException(message=f"Unable to initialize AppodusClient: {e.__str__()}")

        return self

    @property
    def messaging(self) -> MessageClient:
        return self._require_initialized(self._message_client, "messaging")

    @property
    def contract(self) -> ContractClient:
        return self._require_initialized(self._contract_client, "contract")

    @property
    def document(self) -> DocumentClient:
        return self._require_initialized(self._document_client, "document")

    @property
    def chatbot(self) -> ChatbotClient:
        return self._require_initialized(self._chatbot_client, "chatbot")

    def _load_config(self) -> None:
        if not self._appodus_service_url:
            self._appodus_service_url = Utils.get_from_env_fail_if_not_exists('APPODUS_SERVICES_URL')
        if not self._client_id:
            self._client_id = Utils.get_from_env_fail_if_not_exists('APPODUS_CLIENT_ID')
        if not self._client_secret:
            self._client_secret = Utils.get_from_env_fail_if_not_exists('APPODUS_CLIENT_SECRET')

    def _create_client_utils(self) -> None:
        self.client_utils = AppodusClientUtils(
            client_id=self._client_id,
            client_secret=self._client_secret,
            api_version=self._api_version.value,
            http_client=self._http_client
        )

    def _init_clients(self) -> None:
        self._message_client = MessageClient(
            message_manager_url=self._appodus_service_url,
            client_utils=self.client_utils
        )
        self._contract_client = ContractClient(
            contract_manager_url=self._appodus_service_url,
            client_utils=self.client_utils
        )
        self._document_client = DocumentClient(
            document_manager_url=self._appodus_service_url,
            client_utils=self.client_utils
        )
        self._chatbot_client = ChatbotClient(
            chatbot_manager_url=self._appodus_service_url,
            client_utils=self.client_utils
        )

    async def _check_service_health(self) -> None:
        error_message = f"The provided APPODUS_SERVICES_URL '{self._appodus_service_url}' is not reachable"
        try:
            response = await self._http_client.get(f"{self._appodus_service_url}/health")
            if response.status_code != status.HTTP_200_OK:
                raise InternalServerException(
                    message=f"The provided APPODUS_SERVICES_URL '{self._appodus_service_url}' is not reachable."
                )

            response.raise_for_status()
        except ReadTimeout as re:
            error_message = f"{error_message}: Request timeout"
            raise InternalServerException(
                message=error_message
            )
        except Exception as e:
            error_message = f"{error_message}: {e.__str__()}"
            raise InternalServerException(
                message=error_message
            )


    @staticmethod
    def _require_initialized(client, name: str):
        if client is None:
            raise InternalServerException(
                f"AppodusClient.{name} not initialized. Call `await client.init()` first."
            )
        return client
