from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder

from appodus_utils.domain.document.models import CreateDocumentDto, FileDto, DocumentMetadata
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class DocumentClient:
    def __init__(self, document_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._document_manager_url = document_manager_url

    async def upload_document(self, document_metadata: CreateDocumentDto, document: UploadFile) -> FileDto:
        endpoint = f"{self._document_manager_url}/{self._client_utils.get_api_version}/documents"
        document_metadata_json = jsonable_encoder(document_metadata)
        headers = self._client_utils.auth_headers("post", f"{endpoint}", document_metadata_json)
        files = {
            "document": (document.filename, document.file, document.content_type)
        }
        response = await self._client_utils.get_http_client.post(f"{endpoint}",
                                                                 files=files,
                                                                 data=document_metadata_json,
                                                                 headers=headers
                                                                 )
        response.raise_for_status()
        response = response.json()
        return FileDto(**response)

    async def get_document_url(self, doc_id: str, signed: bool = False, signed_expires: int = 3600) -> str:
        endpoint = f"{self._document_manager_url}/{self._client_utils.get_api_version}/documents/{doc_id}"
        headers = self._client_utils.auth_headers("get", f"{endpoint}")
        params = {
            "signed": signed,
            "signed_expires": signed_expires
        }
        response = await self._client_utils.get_http_client.get(endpoint,
                                                                headers=headers,
                                                                params=params
                                                                )
        response.raise_for_status()
        return response.json()


    async def stream_document(self, doc_id: str):
        endpoint = f"{self._document_manager_url}/{self._client_utils.get_api_version}/documents/{doc_id}/stream"
        headers = self._client_utils.auth_headers("get", f"{endpoint}")
        response = await self._client_utils.get_http_client.get(endpoint,
                                                                headers=headers,
                                                                )
        response.raise_for_status()
        return response.json()


    async def update_extras(self, doc_id: str, extras: DocumentMetadata) -> bool:
        endpoint = f"{self._document_manager_url}/{self._client_utils.get_api_version}/documents/{doc_id}"
        headers = self._client_utils.auth_headers("patch", f"{endpoint}")
        response = await self._client_utils.get_http_client.patch(endpoint,
                                                                  json=extras.model_dump(),
                                                                  headers=headers,
                                                                  )
        response.raise_for_status()
        return response.json()

    async def delete_document(self, doc_id: str) -> bool:
        endpoint = f"{self._document_manager_url}/{self._client_utils.get_api_version}/documents/{doc_id}"
        headers = self._client_utils.auth_headers("delete", f"{endpoint}")
        response = await self._client_utils.get_http_client.delete(endpoint,
                                                                headers=headers,
                                                                )
        response.raise_for_status()
        return response.json()
