from unittest import IsolatedAsyncioTestCase

import respx
from _pytest.monkeypatch import MonkeyPatch
from kink import di

from appodus_utils.integrations.messaging.models import MessageRequest, MessageChannel, MessageRequestRecipient, \
    EmailPayload, EmailParty, BatchResult
from fastapi.encoders import jsonable_encoder

from appodus_utils import Utils
from appodus_utils.sdk.appodus_sdk.appodus import AppodusClient
from appodus_utils.sdk.appodus_sdk.services.message_client import MessageClient
from tests.appodus_utils.test_utils import mock_http_request


class TestAppodusMessageClient(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.appodus_client: AppodusClient = di[AppodusClient]
        self.monkeypatch = MonkeyPatch()
        appodus_service_url = Utils.get_from_env_fail_if_not_exists('APPODUS_SERVICES_URL')
        self.url_endpoint = f"{appodus_service_url}/v1/messages"
        self.health_check_endpoint = f"{appodus_service_url}/health"


    async def asyncTearDown(self):
        self.monkeypatch.undo()

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_send_bulk(self):
        # PREPARE
        message_client: MessageClient = self.appodus_client.messaging

        message_request = (MessageRequest.builder()
                           .channel(MessageChannel.EMAIL)
                           .to(MessageRequestRecipient(
            user_id="user_id",
            fullname="Kingsley Ezenwere",
            email="kingsley.ezenwere@gmail.com"
        ))
                           .payload(
            EmailPayload(
                html="<strong>Appodus Email Test drive</strong>",
                subject="Hello from appodus",
                email_from=EmailParty(email="festus.ezenwere@gmail.com", fullname="Festus Ezenwere"),
                reply_to=EmailParty(email="appodus@gmail.com", fullname="appodus global")
            )).build())

        payload = [message_request]

        requests_json = jsonable_encoder(payload)
        self.url_endpoint = f"{self.url_endpoint}"
        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            self.url_endpoint,
            requests_json
        )

        return_json = BatchResult(
            total=1,
            successes=["pass"],
            failures=["fail"],
            processing_time=323432
        )

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.url_endpoint,
            http_method="post",
            request_headers=request_headers,
            return_json=return_json.model_dump(),
            _json=requests_json
        )

        client_response = await message_client.send_bulk(message_requests=payload)

        self.assertEqual(return_json, client_response)
