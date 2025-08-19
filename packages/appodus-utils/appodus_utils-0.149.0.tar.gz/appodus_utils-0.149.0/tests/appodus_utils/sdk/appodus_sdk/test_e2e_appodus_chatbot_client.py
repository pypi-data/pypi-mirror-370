import enum
import json
from unittest import IsolatedAsyncioTestCase

import respx
from _pytest.monkeypatch import MonkeyPatch
from kink import di
from polyfactory.factories.pydantic_factory import ModelFactory


from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils import Utils
from appodus_utils.db.models import SuccessResponse, Page
from appodus_utils.domain.bot.chat.history.models import SearchChatHistoryDto, QueryChatHistoryDto
from appodus_utils.domain.bot.chat.models import SearchChatSessionDto, QueryChatSessionDto
from appodus_utils.domain.bot.models import CreateChatBotDto, UpdateChatBotDto, BotChatOnceDto, BotChatDto, \
    QueryChatBotDto, ChatResponseDto
from appodus_utils.sdk.appodus_sdk.appodus import AppodusClient
from appodus_utils.sdk.appodus_sdk.services.chatbot_client import ChatbotClient
from tests.appodus_utils.test_utils import mock_http_request


class TestAppodusChatbotClient(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.appodus_client: AppodusClient = di[AppodusClient]
        self.monkeypatch = MonkeyPatch()
        appodus_service_url = Utils.get_from_env_fail_if_not_exists('APPODUS_SERVICES_URL')
        self.url_endpoint = f"{appodus_service_url}/v1/bots"
        self.health_check_endpoint = f"{appodus_service_url}/health"
        self.project = "project"


    async def asyncTearDown(self):
        self.monkeypatch.undo()
        # await self.appodus_client.client_utils.get_http_client.aclose()

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_create_chatbot(self):
        # PREPARE
        
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        payload = CreateChatBotDto(
            project=self.project,
            bot_name="bot_name",
            bot_persona="bot_persona",
            bot_intro_message="bot_intro_message",
            bot_tone_and_voice="bot_tone_and_voice",
            restrict_to_provided_info=False,
            your_brand_name="your_brand_name",
            about_your_brand="about_your_brand"
        )

        self.url_endpoint = f"{self.url_endpoint}"
        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            self.url_endpoint,
            payload.model_dump()
        )

        return_json: SuccessResponse[QueryChatBotDto] = SuccessResponse[QueryChatBotDto](
                success=True,
                message="Query processed successfully",
                data=QueryChatBotDto(**payload.model_dump(), client_id="client_id")
        )
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.url_endpoint,
            http_method="post",
            request_headers=request_headers,
            return_json=return_json.model_dump(),
            _json=payload.model_dump(),
        )

        # ACT
        client_response = await chatbot_client.create_chatbot(create_dto=payload)

        # ASSERT
        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_update_chatbot(self):
        # PREPARE
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        update_dto = UpdateChatBotDto(
            bot_name="Updated Bot"
        )

        url_endpoint = f"{self.url_endpoint}/{self.project}"

        request_headers = self.appodus_client.client_utils.auth_headers(
            "patch",
            url_endpoint,
            body=update_dto.model_dump()
        )

        return_json = True
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="patch",
            request_headers=request_headers,
            return_json=return_json,
            _json=update_dto.model_dump()
        )

        # ACT
        client_response = await chatbot_client.update_chatbot(
            project=self.project,
            update_dto=update_dto
        )

        # ASSERT
        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_bot_chat_once(self):
        # PREPARE
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        payload = BotChatOnceDto(
            context="You are a helpful assistant.",
            message="What is appodus?"
        )

        url_endpoint = f"{self.url_endpoint}/chat-once"

        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            url_endpoint,
            body=payload.model_dump()
        )

        return_json = ChatResponseDto(
            answer="Chat answer",
            session_id="session_id"
        )
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="post",
            request_headers=request_headers,
            return_json=return_json.model_dump(),
            _json=payload.model_dump()
        )

        # ACT
        client_response = await chatbot_client.bot_chat_once(
            chat_dto=payload
        )

        # ASSERT
        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_bot_chat(self):
        # PREPARE
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        session_id = "session_id"
        payload = BotChatDto(
            project=self.project,
            message="Hello, how do I stay thick?",
            position=1
        )

        url_endpoint = f"{self.url_endpoint}/chats/{session_id}"

        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            url_endpoint,
            body=payload.model_dump()
        )

        return_json = ChatResponseDto(
            answer="Chat answer",
            session_id="session_id"
        )
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="post",
            request_headers=request_headers,
            return_json=return_json.model_dump(),
            _json=payload.model_dump()
        )

        # ACT
        client_response = await chatbot_client.bot_chat(
            session_id=session_id,
            chat_dto=payload
        )

        # ASSERT
        self.assertEqual(return_json, client_response)


    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_get_chat_session_page(self):
        # PREPARE
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        search_dto = SearchChatSessionDto(
            page=0,
            page_size=10
        )
        search_params = {
            key: (value.value if isinstance(value, enum.Enum) else value)
            for key, value in search_dto.model_dump(exclude_none=True).items()
        }

        url_endpoint = f"{self.url_endpoint}/chats"


        request_headers = self.appodus_client.client_utils.auth_headers(
            "get",
            url_endpoint,
            body=search_params
        )


        return_obj: Page[QueryChatSessionDto] = QueryChatSessionPageFactory.build()
        return_json = json.dumps(return_obj.model_dump(), default=str)

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="get",
            request_headers=request_headers,
            return_json=json.loads(return_json),
            _params=search_params
        )

        # ACT
        client_response = await chatbot_client.get_chat_session_page(
            search_dto=search_dto
        )

        # ASSERT
        self.assertEqual(return_obj, client_response)



    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_get_chat_history_page(self):
        # PREPARE
        chatbot_client: ChatbotClient = self.appodus_client.chatbot

        search_dto = SearchChatHistoryDto(
            page=0,
            page_size=10
        )
        search_params = {
            key: (value.value if isinstance(value, enum.Enum) else value)
            for key, value in search_dto.model_dump(exclude_none=True).items()
        }

        session_id = "session_id"
        url_endpoint = f"{self.url_endpoint}/chats/{session_id}"


        request_headers = self.appodus_client.client_utils.auth_headers(
            "get",
            url_endpoint,
            body=search_params
        )
        return_obj: Page[QueryChatHistoryDto] = QueryChatHistoryPageFactory.build()
        return_json = json.dumps(return_obj.model_dump(), default=str)
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="get",
            request_headers=request_headers,
            return_json=json.loads(return_json),
            _params=search_params
        )

        # ACT
        client_response = await chatbot_client.get_chat_history_page(
            session_id=session_id,
            search_dto=search_dto
        )

        # ASSERT
        self.assertEqual(return_obj, client_response)



# OBJECT FAKER FACTORIES using polyfactory
# QueryChatSessionDto
class QueryChatSessionDtoFactory(ModelFactory[QueryChatSessionDto]):
    __model__ = QueryChatSessionDto
    __check_model__ = False

class QueryChatSessionPageFactory(ModelFactory[Page[QueryChatSessionDto]]):
    __model__ = Page[QueryChatSessionDto]
    __check_model__ = False

# QueryChatHistoryDto
class QueryChatHistoryDtoFactory(ModelFactory[QueryChatHistoryDto]):
    __model__ = QueryChatHistoryDto
    __check_model__ = False

class QueryChatHistoryPageFactory(ModelFactory[Page[QueryChatHistoryDto]]):
    __model__ = Page[QueryChatHistoryDto]
    __check_model__ = False