from typing import List

from kink import di

from appodus_utils.integrations.messaging.models import MessageRequest, BatchResult
from appodus_utils.sdk.appodus_sdk.services.messages.messaging_service import MessagingService
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class MessageClient:
    def __init__(self, message_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._message_manager_url = message_manager_url
        self.messaging_service = MessagingService(
            message_manager_url=message_manager_url,
            client_utils=client_utils
        )

        # Provide for further injection by builder style message sender
        di[MessagingService] = lambda _di: self.messaging_service

    async def send_bulk(self, message_requests: List[MessageRequest]) -> BatchResult:
        return await self.messaging_service.send_bulk(message_requests=message_requests)

    async def send_message(self, message_request: MessageRequest) -> BatchResult:
        return await self.messaging_service.send_message(message_request=message_request)
