from fastapi.encoders import jsonable_encoder

from appodus_utils.domain.contract.models import GenerateAndSendSignDto
from appodus_utils.integrations.document_sign.models import SignRequestResponseDto
from appodus_utils.sdk.appodus_sdk.utils import AppodusClientUtils


class ContractClient:
    def __init__(self, contract_manager_url: str, client_utils: AppodusClientUtils):
        self._client_utils = client_utils
        self._contract_manager_url = f"{contract_manager_url}/{client_utils.get_api_version}/contracts"

    async def generate_and_send_sign_request(self, request_dto: GenerateAndSendSignDto) -> SignRequestResponseDto:
        endpoint = f"{self._contract_manager_url}"
        message_requests_data = jsonable_encoder(request_dto)
        headers = self._client_utils.auth_headers("post", f"{endpoint}", message_requests_data)
        response = await self._client_utils.get_http_client.post(f"{endpoint}", json=message_requests_data, headers=headers)
        response.raise_for_status()

        response = response.json()
        return SignRequestResponseDto(**response)

    async def get_signer_embedded_sign_url(self, signer_email: str) -> str:
        endpoint = f"{self._contract_manager_url}/signers/{signer_email}/embedded"
        headers = self._client_utils.auth_headers("get", f"{endpoint}", {})
        response = await self._client_utils.get_http_client.get(f"{endpoint}", headers=headers)
        response.raise_for_status()

        return response.json()
