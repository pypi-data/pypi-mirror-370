import typing
from typing import Union

import httpx
import respx
from _pytest.monkeypatch import MonkeyPatch
from fastapi import BackgroundTasks
from httpx import AsyncClient, Response, Request
from httpx._types import HeaderTypes, RequestData, RequestFiles
from kink import di
from libre_fastapi_jwt import AuthJWT
from respx.types import QueryParamTypes

from appodus_utils.domain.user.auth.active_auditor.models import ActiveAuditor
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.domain.user.models import QueryUserDto
from appodus_utils.integrations.messaging.models import BatchResult


def mock_http_client(monkeypatch: MonkeyPatch, http_client: AsyncClient, request_url: str):

    # Mock POST request to utils_settings.APPODUS_SERVICES_URL
    return_json = BatchResult(
        total=1,
        successes=["pass"],
        failures=["fail"],
        processing_time=323432
    )

    async def mock_request(
            url: str,
            *,
            params: QueryParamTypes | None = None,
            json: typing.Any | None = None,
            data: RequestData | None = None,
            files: RequestFiles | None = None,
            headers: HeaderTypes | None = None
    ):

        return Response(200, json=return_json.model_dump(), request=Request("POST", request_url))

    monkeypatch.setattr(http_client, "post", mock_request)


def mock_http_request(monkeypatch: MonkeyPatch, http_client: AsyncClient, request_url: str, http_method: str, request_headers: dict,
                      return_json: Union[dict, str, bool] = None,
                     _params: QueryParamTypes | None = None,
                     _json: typing.Any | None = None,
                     _data: RequestData | None = None,
                     _files: RequestFiles | None = None,
                     ):

    return_json = return_json or {"message": "success"}

    async def mock_request(
            url: str,
            *,
            params: QueryParamTypes | None = None,
            json: typing.Any | None = None,
            data: RequestData | None = None,
            files: RequestFiles | None = None,
            headers: HeaderTypes | None = None
    ):
        assert url == request_url
        assert headers["X-Client-ID"] == request_headers["X-Client-ID"]
        if _params:
            assert params == _params
        if _json:
            assert json == _json
        if _data:
            assert data == _data
        if _files:
            assert files == _files

        return Response(200, json=return_json, request=Request(http_method, request_url))

    monkeypatch.setattr(http_client, http_method, mock_request)

# Register this in your test setup
def mock_active_auditor_service(monkeypatch: MonkeyPatch, user: QueryUserDto, background_tasks: BackgroundTasks = None):
    active_auditor_service = di[ActiveAuditorService]

    # get_authorizer_from_context
    async def mock_get_authorizer_from_context() -> AuthJWT:
        return AuthJWT()
    monkeypatch.setattr(active_auditor_service, "get_authorizer_from_context", mock_get_authorizer_from_context)

    # get_combined_authorizer_from_context
    async def mock_get_combined_authorizer_from_context():
        return ActiveAuditor.model_copy(user), MockAuthorizer(user_id=user.id)
    monkeypatch.setattr(active_auditor_service, "get_combined_authorizer_from_context", mock_get_combined_authorizer_from_context)

    # get_background_tasks_from_context
    async def mock_get_background_tasks_from_context():
        return background_tasks
    monkeypatch.setattr(active_auditor_service, "get_background_tasks_from_context", mock_get_background_tasks_from_context)


class MockAuthorizer:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def jwt_required(self):
        pass  # or raise if needed

    def fresh_jwt_required(self):
        pass  # or raise if needed

    def get_jwt_subject(self):
        return self.user_id

    def get_raw_jwt(self):
        return {"jti": "our_jti"}

    def unset_jwt_cookies(self):
        pass

    def create_access_token(self, subject, expires_time, user_claims):
        return "a token"

    def create_refresh_token(self, subject, expires_time, user_claims):
        pass

    def set_access_cookies(self, access_token):
        pass

    def jwt_refresh_token_required(self):
        pass
