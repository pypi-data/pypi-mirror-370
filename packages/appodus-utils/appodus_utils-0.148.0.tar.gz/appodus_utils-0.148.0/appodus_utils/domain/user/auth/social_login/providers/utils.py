import urllib.parse
from logging import Logger
from urllib.parse import urlunparse, urlparse

from kink import di
from starlette.requests import Request

from appodus_utils import Utils
from appodus_utils.common.auth_utils import JwtAuthUtils
from appodus_utils.common.client_utils import ClientUtils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.domain.user.auth.models import SocialAuthOperationType
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform, OAuthRequestStoredState

logger: Logger = di["logger"]


@decorate_all_methods(method_trace_logger)
class OauthUtils:

    @staticmethod
    async def init_0auth(platform: SocialAuthPlatform, request: Request, base_url: str, client_id: str, scope: str, operation_type: SocialAuthOperationType) -> dict:
        code_challenge, code_verifier, state = JwtAuthUtils.generate_pkce()
        redirect_uri = await OauthUtils.get_auth_redirect_url(platform=platform, request=request)

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        frontend_origin = request.headers.get("referer")

        oauth_request = OAuthRequestStoredState(
            code_verifier=code_verifier,
            operation_type=operation_type,
            redirect_uri=redirect_uri,
            frontend_origin=frontend_origin
        )
        await RedisUtils.set_redis(state, oauth_request)

        query_string = urllib.parse.urlencode(params)
        return {
            "url": f"{base_url}?{query_string}",
            "code_verifier": code_verifier
        }

    @staticmethod
    async def get_auth_redirect_url(platform: SocialAuthPlatform, request: Request) -> str:
        """
        The redirect url is similar to the init url, when we remove the tailing /init
        :param platform:
        :param request:
        :return:
        """
        # Parse the incoming URL parts
        base_path = request.url.path.rsplit("/", 1)[0] + "/" # Remove the /init in '/v1/users/auths/socials/google/init'
        base_path = f"/api{base_path}" # We're redirecting to our proxy first (NextJS or any other)

        # Use our proxy origin e.g http://appodus.com
        referer_url = request.headers.get("referer")
        parsed_referer_url = urlparse(referer_url)

        full_url = urlunparse((
            parsed_referer_url.scheme,
            parsed_referer_url.netloc,
            base_path,
            "",  # params
            "",  # query
            ""  # fragment
        ))

        return full_url
