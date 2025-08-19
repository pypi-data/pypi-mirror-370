from httpx import AsyncClient
from jose import jwt
from kink import di, inject
from starlette.requests import Request

from appodus_utils import Utils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.domain.user.auth.models import SocialAuthOperationType, OAuthCallbackRequest, SocialLoginUserInfo
from appodus_utils.domain.user.auth.social_login.interface import ISocialAuthProvider
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform
from appodus_utils.domain.user.auth.social_login.providers.utils import OauthUtils

httpx_client: AsyncClient = di[AsyncClient]

@inject
@decorate_all_methods(method_trace_logger)
class GoogleAuthProvider(ISocialAuthProvider):
    def __init__(self):
        self._client_id = Utils.get_from_env_fail_if_not_exists("GOOGLE_CLIENT_ID")
        self._client_secret = Utils.get_from_env_fail_if_not_exists("GOOGLE_CLIENT_SECRET")
        self._auth_base_url = Utils.get_from_env_fail_if_not_exists("GOOGLE_AUTH_BASE_URL")

    @property
    def platform(self):
        return SocialAuthPlatform.GOOGLE

    async def initialize(self, operation_type: SocialAuthOperationType, request: Request) -> dict:
        scope = "openid email profile"

        return await OauthUtils.init_0auth(self.platform, request, self._auth_base_url, self._client_id, scope, operation_type)

    async def verify(self, payload: OAuthCallbackRequest, request: Request) -> SocialLoginUserInfo:
        token_response = await httpx_client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": payload.code,
                "grant_type": "authorization_code",
                "redirect_uri": payload.redirect_uri,
                "code_verifier": payload.code_verifier,
            }
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        id_token = tokens["id_token"]
        claims = jwt.get_unverified_claims(id_token)

        if claims["aud"] != self._client_id:
            raise ValueError("Invalid audience")

        return SocialLoginUserInfo(
            id=claims["sub"],
            email=claims["email"],
            firstname=claims["given_name"],
            lastname=claims["family_name"],
            exp=claims["exp"],
            operation_type=payload.operation_type,
            frontend_origin=payload.frontend_origin
        )
