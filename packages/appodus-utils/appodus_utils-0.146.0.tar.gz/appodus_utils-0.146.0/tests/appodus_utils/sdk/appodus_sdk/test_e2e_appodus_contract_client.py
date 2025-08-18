from unittest import IsolatedAsyncioTestCase

import respx
from _pytest.monkeypatch import MonkeyPatch
from fastapi.encoders import jsonable_encoder
from kink import di

from appodus_utils import Utils

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.domain.contract.models import GenerateAndSendSignDto
from appodus_utils.integrations.document_sign.models import Signer, SignActionType, DocumentVerificationType, \
    SignRequestResponseDto
from appodus_utils.sdk.appodus_sdk.appodus import AppodusClient
from appodus_utils.sdk.appodus_sdk.services.contract_client import ContractClient
from tests.appodus_utils.test_utils import mock_http_request


class TestAppodusContractClient(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.appodus_client: AppodusClient = di[AppodusClient]
        self.monkeypatch = MonkeyPatch()
        appodus_service_url = Utils.get_from_env_fail_if_not_exists('APPODUS_SERVICES_URL')
        self.url_endpoint = f"{appodus_service_url}/v1/contracts"
        self.health_check_endpoint = f"{appodus_service_url}/health"


    async def asyncTearDown(self):
        self.monkeypatch.undo()
        # await self.appodus_client.client_utils.get_http_client.aclose()

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_generate_and_send_sign_request(self):
        # PREPARE
        contract_client: ContractClient = self.appodus_client.contract

        payload = GenerateAndSendSignDto(
            template_id="template_id",
            template_variables={
                "Agreement_Date": Utils.datetime_now_format(output_format="%d/%m/%Y"),
                "Appodus_Address": "23 Agodogba Street, Parkview, Ikoyi, Lagos NG.",
                "Client_Company_Name": "Arone Technologies Limited",
                "Client_Address": "4 Mbanefo Street, New Haven, Enugu",
                "Client_Phone": "2348056453738",
                "Client_Email": "kingsley.ezenwere@gmail.com"
            },
            contract_id="contract_id",
            signers=[
                Signer(
                    action_type=SignActionType.SIGN,
                    recipient_email="kingsley.ezenwere@gmail.com",
                    recipient_phonenumber="+2347039018727",
                    recipient_name="Kingsley Ezenwere",
                    verify_recipient=True,
                    verification_type=DocumentVerificationType.EMAIL,
                    signing_order=0
                )
            ],
            signing_client_name="Gabrielle"
        )
        requests_json = jsonable_encoder(payload)
        self.url_endpoint = f"{self.url_endpoint}"
        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            self.url_endpoint,
            requests_json
        )

        return_json = SignRequestResponseDto(
            request_id="request_id",
            signers=payload.signers
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

        client_response = await contract_client.generate_and_send_sign_request(request_dto=payload)

        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_get_signer_embedded_sign_url(self):
        # PREPARE
        contract_client: ContractClient = self.appodus_client.contract
        signer_email = "kingsley.ezenwere@gmail.com"
        request_headers = self.appodus_client.client_utils.auth_headers(
            "get",
            f"{self.url_endpoint}"
        )
        self.url_endpoint = f"{self.url_endpoint}/signers/{signer_email}/embedded"

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.url_endpoint,
            http_method="get",
            request_headers=request_headers
        )

        await contract_client.get_signer_embedded_sign_url(signer_email=signer_email)
