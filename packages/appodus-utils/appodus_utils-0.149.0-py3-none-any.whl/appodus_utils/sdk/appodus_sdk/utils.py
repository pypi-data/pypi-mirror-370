from httpx import AsyncClient

from appodus_utils.common.client_utils import ClientUtils


class AppodusClientUtils:

    def __init__(self, client_id: str, client_secret: str, api_version: str, http_client: AsyncClient):
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_version = api_version
        self._http_client = http_client

    @property
    def get_api_version(self):
        return self._api_version

    @property
    def get_http_client(self):
        return self._http_client

    def auth_headers(self, method: str, path: str, body: dict = None) -> dict:
        return ClientUtils.create_auth_headers(
            client_id=self._client_id,
            client_secret=self._client_secret,
            method=method,
            path=path,
            body=body
        )
