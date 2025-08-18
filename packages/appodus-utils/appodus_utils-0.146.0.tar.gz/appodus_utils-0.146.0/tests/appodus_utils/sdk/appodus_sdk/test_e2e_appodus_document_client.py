from unittest import IsolatedAsyncioTestCase

import respx
from _pytest.monkeypatch import MonkeyPatch
from fastapi.encoders import jsonable_encoder
from httpx import Response, Request
from kink import di


from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils.common.appodus_test_utils import TestUtils
from appodus_utils.domain.document.models import CreateDocumentDto, DocumentAccessScope, DocumentMetadata, FileDto
from appodus_utils.sdk.appodus_sdk.appodus import AppodusClient
from appodus_utils.sdk.appodus_sdk.services.document_client import DocumentClient
from tests.appodus_utils.test_utils import mock_http_request


class TestAppodusDocumentClient(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.appodus_client: AppodusClient = di[AppodusClient]
        self.monkeypatch = MonkeyPatch()
        appodus_service_url = utils_settings.APPODUS_SERVICES_URL
        self.url_endpoint = f"{appodus_service_url}/v1/documents"
        self.health_check_endpoint = f"{appodus_service_url}/health"
        self.doc_id = "doc_id"
        self.doc_id_endpoint = f"{self.url_endpoint}/{self.doc_id}"


        self.upload_file = TestUtils.create_mock_upload_file()


    async def asyncTearDown(self):
        self.monkeypatch.undo()
        # await self.appodus_client.client_utils.get_http_client.aclose()

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_upload_document(self):
        # PREPARE
        document_client: DocumentClient = self.appodus_client.document

        file = self.upload_file
        request_files = {
            "document": (file.filename, file.file, file.content_type)
        }
        payload = CreateDocumentDto(
            store_key="contracts/contract_uihef/user_jhdhw.pdf",
            access_scope=DocumentAccessScope.PRIVATE,
            extras=DocumentMetadata(
                tags=["tag1", "tag2"],
                owner="Kingsley Ezenwere",
                description="Test document",
            ).model_dump()
        )

        requests_data = jsonable_encoder(payload)
        self.url_endpoint = f"{self.url_endpoint}"
        request_headers = self.appodus_client.client_utils.auth_headers(
            "post",
            self.url_endpoint,
            requests_data
        )

        return_json = FileDto(
            url="https://aws.com/document/url",
            document_id="kjkfhkjfhdjkhkjdshjkdhfdggfgdfg"
        )

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.url_endpoint,
            http_method="post",
            request_headers=request_headers,
            return_json=return_json.model_dump(),
            _data=requests_data,
            _files=request_files
        )

        client_response = await document_client.upload_document(document_metadata=payload, document=file)

        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_get_document_url(self):
        # PREPARE
        document_client: DocumentClient = self.appodus_client.document

        signed = True
        signed_expires = 6000
        params = {
            "signed": signed,
            "signed_expires": signed_expires
        }


        request_headers = self.appodus_client.client_utils.auth_headers(
            "get",
            self.doc_id_endpoint
        )
        return_json = "https://aws.com/document/url"

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.doc_id_endpoint,
            http_method="get",
            request_headers=request_headers,
            return_json=return_json,
            _params=params
        )

        client_response = await document_client.get_document_url(
            doc_id=self.doc_id,
            signed= signed,
            signed_expires = signed_expires
        )

        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_stream_document(self):
        # PREPARE
        document_client: DocumentClient = self.appodus_client.document

        url_endpoint = f"{self.doc_id_endpoint}/stream"

        request_headers = self.appodus_client.client_utils.auth_headers(
            "get",
            url_endpoint
        )

        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=url_endpoint,
            http_method="get",
            request_headers=request_headers
        )

        await document_client.stream_document(
            doc_id=self.doc_id
        )

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_update_extras(self):
        # PREPARE
        document_client: DocumentClient = self.appodus_client.document

        payload = DocumentMetadata(
            tags=["tag1", "tag2"],
            owner="Kingsley Ezenwere",
            description="The description"
        )

        request_headers = self.appodus_client.client_utils.auth_headers(
            "patch",
            self.doc_id_endpoint,
            body=payload.model_dump()
        )
        return_json = True
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.doc_id_endpoint,
            http_method="patch",
            request_headers=request_headers,
            return_json=return_json,
            _json=payload.model_dump()
        )

        client_response = await document_client.update_extras(
            doc_id=self.doc_id,
            extras=payload
        )

        self.assertEqual(return_json, client_response)

    @respx.mock(assert_all_called=False, assert_all_mocked=False)
    async def test_delete_document(self):
        # PREPARE
        document_client: DocumentClient = self.appodus_client.document


        request_headers = self.appodus_client.client_utils.auth_headers(
            "delete",
            self.doc_id_endpoint
        )
        return_json=True
        mock_http_request(
            monkeypatch=self.monkeypatch,
            http_client=self.appodus_client.client_utils.get_http_client,
            request_url=self.doc_id_endpoint,
            http_method="delete",
            request_headers=request_headers,
            return_json=return_json
        )

        client_response = await document_client.delete_document(
            doc_id=self.doc_id
        )

        self.assertEqual(return_json, client_response)
