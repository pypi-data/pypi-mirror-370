import json
from typing import List

from fastapi.encoders import jsonable_encoder

from appodus_utils.integrations.messaging.models import MessageRequest, BatchResult
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class MessagingService:
    def __init__(self, message_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._message_manager_url = message_manager_url

    async def send_message(self, message_request: MessageRequest) -> BatchResult:
        return await self.send_bulk([message_request])

    async def send_bulk(self, message_requests: List[MessageRequest]) -> BatchResult:
        endpoint = f"{self._message_manager_url}/{self._client_utils.get_api_version}/messages"
        message_requests_data = jsonable_encoder(message_requests)
        headers = self._client_utils.auth_headers("post", f"{endpoint}", message_requests_data)
        response = await self._client_utils.get_http_client.post(f"{endpoint}", json=message_requests_data, headers=headers)
        response.raise_for_status()

        print(f"response text: {response.text}")
        response = response.json()
        return BatchResult(**response)
