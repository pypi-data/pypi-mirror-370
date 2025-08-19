import enum

from appodus_utils.db.models import SuccessResponse, Page
from appodus_utils.domain.bot.chat.history.models import SearchChatHistoryDto, QueryChatHistoryDto
from appodus_utils.domain.bot.chat.models import SearchChatSessionDto, QueryChatSessionDto
from appodus_utils.domain.bot.models import CreateChatBotDto, QueryChatBotDto, UpdateChatBotDto, BotChatOnceDto, \
    ChatResponseDto, BotChatDto
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class ChatbotClient:
    def __init__(self, chatbot_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._chatbot_manager_url = chatbot_manager_url
        self.endpoint = f"{self._chatbot_manager_url}/{self._client_utils.get_api_version}/bots"

    async def create_chatbot(self, create_dto: CreateChatBotDto) -> SuccessResponse[QueryChatBotDto]:
        endpoint = f"{self.endpoint}"
        headers = self._client_utils.auth_headers("post", f"{endpoint}", create_dto.model_dump())
        response = await self._client_utils.get_http_client.post(f"{endpoint}", json=create_dto.model_dump(), headers=headers)
        response.raise_for_status()

        response = response.json()
        return SuccessResponse[QueryChatBotDto].model_validate(response)

    async def update_chatbot(self, project: str, update_dto: UpdateChatBotDto) -> bool:
        endpoint = f"{self.endpoint}/{project}"
        headers = self._client_utils.auth_headers("patch", f"{endpoint}", update_dto.model_dump())
        response = await self._client_utils.get_http_client.patch(endpoint, json=update_dto.model_dump(), headers=headers)
        response.raise_for_status()

        return response.json()

    async def bot_chat_once(self, chat_dto: BotChatOnceDto) -> ChatResponseDto:
        endpoint = f"{self.endpoint}/chat-once"
        headers = self._client_utils.auth_headers("post", f"{endpoint}", chat_dto.model_dump())
        response = await self._client_utils.get_http_client.post(endpoint, json=chat_dto.model_dump(), headers=headers)
        response.raise_for_status()

        response = response.json()
        return ChatResponseDto.model_validate(response)

    async def bot_chat(self, session_id: str,  chat_dto: BotChatDto) -> ChatResponseDto:
        endpoint = f"{self.endpoint}/chats/{session_id}"
        headers = self._client_utils.auth_headers("post", f"{endpoint}", chat_dto.model_dump())
        response = await self._client_utils.get_http_client.post(endpoint, json=chat_dto.model_dump(), headers=headers)
        response.raise_for_status()


        response = response.json()
        return ChatResponseDto.model_validate(response)

    async def get_chat_session_page(self, search_dto: SearchChatSessionDto) -> Page[QueryChatSessionDto]:
        endpoint = f"{self.endpoint}/chats"
        search_params = {
            key: (value.value if isinstance(value, enum.Enum) else value)
            for key, value in search_dto.model_dump(exclude_none=True).items()
        }
        headers = self._client_utils.auth_headers("get", f"{endpoint}", search_params)
        response = await self._client_utils.get_http_client.get(endpoint, headers=headers, params=search_params)
        response.raise_for_status()

        response = response.json()
        return Page[QueryChatSessionDto].model_validate(response)

    async def get_chat_history_page(self, session_id: str, search_dto: SearchChatHistoryDto) -> Page[QueryChatHistoryDto]:
        endpoint = f"{self.endpoint}/chats/{session_id}"
        search_params = {
            key: (value.value if isinstance(value, enum.Enum) else value)
            for key, value in search_dto.model_dump(exclude_none=True).items()
        }
        headers = self._client_utils.auth_headers("get", f"{endpoint}", search_params)
        response = await self._client_utils.get_http_client.get(endpoint, headers=headers, params=search_params)
        response.raise_for_status()

        response = response.json()
        return Page[QueryChatHistoryDto].model_validate(response)
