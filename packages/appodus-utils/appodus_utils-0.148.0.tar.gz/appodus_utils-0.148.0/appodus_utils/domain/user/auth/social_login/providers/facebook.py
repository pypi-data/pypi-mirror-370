from appodus_utils import Utils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from httpx import AsyncClient
from kink import di, inject
from starlette.requests import Request

from appodus_utils.domain.user.auth.models import SocialAuthOperationType, OAuthCallbackRequest, SocialLoginUserInfo
from appodus_utils.domain.user.auth.social_login.interface import ISocialAuthProvider
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform
from appodus_utils.domain.user.auth.social_login.providers.utils import OauthUtils

httpx_client: AsyncClient = di[AsyncClient]

@inject
@decorate_all_methods(method_trace_logger)
class FacebookAuthProvider(ISocialAuthProvider):
    def __init__(self):
        self._client_id = Utils.get_from_env_fail_if_not_exists("FACEBOOK_APP_ID")
        self._client_secret = Utils.get_from_env_fail_if_not_exists("FACEBOOK_APP_SECRET")
        self._auth_base_url = Utils.get_from_env_fail_if_not_exists("FACEBOOK_AUTH_BASE_URL")

    @property
    def platform(self):
        return SocialAuthPlatform.FACEBOOK

    async def initialize(self, operation_type: SocialAuthOperationType, request: Request) -> dict:
        scope = "openid email profile"

        return await OauthUtils.init_0auth(self.platform, request, self._auth_base_url, self._client_id, scope, operation_type)

    async def verify(self, payload: OAuthCallbackRequest, request: Request) -> SocialLoginUserInfo:

        # Exchange code for token
        token_response = await httpx_client.get(
            "https://graph.facebook.com/v22.0/oauth/access_token",
            params={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "redirect_uri": payload.redirect_uri,
                "code": payload.code,
                "code_verifier": payload.code_verifier,
            }
        )
        token_response.raise_for_status()

        # Get user info
        user_response = await httpx_client.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,email,first_name,last_name",
                "access_token": token_response.json()["access_token"]
            }
        )
        user_response.raise_for_status()
        user_info = user_response.json()

        return SocialLoginUserInfo(
            id=user_info["id"],
            email=user_info["email"],
            firstname=user_info["first_name"],
            lastname=user_info["last_name"],
            exp=0,
            operation_type=payload.operation_type,
            frontend_origin=payload.frontend_origin
        )
