# import unittest
# from _pytest.monkeypatch import MonkeyPatch
#
# from appodus_utils.common.appodus_test_utils import TestUtils
#
#
# class TestContractController(unittest.IsolatedAsyncioTestCase):
#
#     async def asyncSetUp(self):
#         self.httpx_client = TestUtils.get_app_test_client(app=fast_api_app)
#         self.httpx_client_endpoint = "/v1/contracts"
#         self.monkeypatch = MonkeyPatch()
#
#     async def asyncTearDown(self):
#         self.monkeypatch.undo()
#         await self._truncate_tables()
#         await self.httpx_client.aclose()
#         await close_db_engine()
#
#     @staticmethod
#     async def _truncate_tables():
#         await TestUtils.truncate_entities([ContractTemplate, FinalContract, ContractSigner])
#
#     async def test_generate_and_sign(self):
#         # Arrange
#         payload = await contract_test__build_generate_and_send_sign_request_payload(
#             monkeypatch=self.monkeypatch,
#             mock_dependencies=True
#         )
#         payload_dict = jsonable_encoder(payload)
#
#         headers = ClientUtils.create_auth_headers(
#             client_id=settings.APPODUS_CLIENT_ID,
#             client_secret=settings.APPODUS_CLIENT_SECRET,
#             method="post",
#             path=self.httpx_client_endpoint,
#             body=payload_dict
#         )
#
#         # ACT
#         response = await self.httpx_client.post(f"{self.httpx_client_endpoint}",
#                                                 json=payload_dict,
#                                                 headers=headers,
#                                                 follow_redirects=True
#                                                 )
#
#         # Assert
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#         self.assertIsNotNone(response.json()["request_id"])
#         self.assertIsNotNone(response.json()["final_contract_id"])
#
#     async def test_generate_and_send_sign_request(self):
#         # Arrange
#         sign_request_response = await contract_test__get_sign_request_response(
#             monkeypatch=self.monkeypatch,
#             mock_dependencies = True
#         )
#         signer_email = sign_request_response.signers[0].recipient_email
#
#         headers = ClientUtils.create_auth_headers(
#             client_id=settings.APPODUS_CLIENT_ID,
#             client_secret=settings.APPODUS_CLIENT_SECRET,
#             method="get",
#             path=self.httpx_client_endpoint,
#             body={}
#         )
#
#         # ACT
#         response = await self.httpx_client.get(f"{self.httpx_client_endpoint}/signers/{signer_email}/embedded",
#                                                 headers=headers,
#                                                 follow_redirects=True
#                                                 )
#
#         # Assert
#         self.assertEqual(status.HTTP_200_OK, response.status_code)
#         self.assertIsNotNone(response.json().endswith("embedtoken?"))