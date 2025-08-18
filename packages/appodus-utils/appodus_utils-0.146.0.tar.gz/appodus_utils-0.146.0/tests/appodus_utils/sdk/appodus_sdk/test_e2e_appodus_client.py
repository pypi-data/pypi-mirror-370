from unittest import IsolatedAsyncioTestCase

import respx
from _pytest.monkeypatch import MonkeyPatch
from kink import di

from appodus_utils import Utils

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.sdk.appodus_sdk.appodus import AppodusClient

class TestAppodusClient(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.appodus_client: AppodusClient = di[AppodusClient]
        appodus_service_url = Utils.get_from_env_fail_if_not_exists('APPODUS_SERVICES_URL')
        self.url_endpoint = f"{appodus_service_url}/health"
        self.monkeypatch = MonkeyPatch()

    async def asyncTearDown(self):
        self.monkeypatch.undo()

    @respx.mock
    async def test_init(self):
        response = self.appodus_client.init()
        self.assertIsInstance(response, AppodusClient)
