from datetime import timedelta

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
class AppleAuthProvider(ISocialAuthProvider):
    def __init__(self):
        self._client_id = Utils.get_from_env_fail_if_not_exists("APPLE_CLIENT_ID")
        self._iss = Utils.get_from_env_fail_if_not_exists("APPLE_TEAM_ID")
        self._auth_base_url = Utils.get_from_env_fail_if_not_exists("APPLE_AUTH_BASE_URL")
        self._private_key = Utils.get_from_env_fail_if_not_exists("APPLE_PRIVATE_KEY")
        self._key_id = Utils.get_from_env_fail_if_not_exists("APPLE_KEY_ID")

    @property
    def platform(self):
        return SocialAuthPlatform.APPLE

    async def initialize(self, operation_type: SocialAuthOperationType, request: Request) -> dict:
        scope = "openid email profile"

        return await OauthUtils.init_0auth(self.platform, request, self._auth_base_url, self._client_id, scope, operation_type)

    async def verify(self, payload: OAuthCallbackRequest, request: Request) -> SocialLoginUserInfo:

        # Generate client secret (JWT)
        client_secret = jwt.encode(
            {
                "iss": self._iss,
                "iat": Utils.datetime_now(),
                "exp": Utils.datetime_now() + timedelta(minutes=5),
                "aud": "https://appleid.apple.com",
                "sub": self._client_id
            },
            self._private_key,
            algorithm="ES256",
            headers={"kid": self._key_id}
        )

        # Exchange code for tokens
        token_response = await httpx_client.post(
            "https://appleid.apple.com/auth/token",
            data={
                "client_id": self._client_id,
                "client_secret": client_secret,
                "code": payload.code,
                "grant_type": "authorization_code",
                "redirect_uri": payload.redirect_uri
            }
        )

        # Verify ID token
        id_token = token_response.json()["id_token"]
        claims = jwt.decode(
            id_token,
            key="self.config.public_key",
            algorithms=["ES256"],
            audience=self._client_id
        )

        return SocialLoginUserInfo(
            email=claims["email"],
            operation_type=payload.operation_type,
            frontend_origin=payload.frontend_origin
        )
