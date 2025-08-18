import base64
import hashlib
import secrets
from datetime import timedelta

from appodus_utils import Utils
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from libre_fastapi_jwt import AuthJWT

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.domain.user.auth.active_auditor.models import ActiveAuditor
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.domain.user.auth.models import TokenType, LoginSuccessDto

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auths/access-token", auto_error=False)

# appodus_settings = Utils.get_from_env_fail_if_not_exists('APPODUS_SETTINGS')
# appodus_settings_dict = json.loads(appodus_settings)
# 
# utils_settings.copy(update=appodus_settings_dict)


class JwtAuthUtils:
    @staticmethod
    @AuthJWT.load_config
    def get_config():
        return utils_settings

    @staticmethod
    @AuthJWT.token_in_denylist_loader
    async def check_if_token_in_denylist(decrypted_token) -> bool:
        jti = decrypted_token['jti']
        entry = await RedisUtils.get_redis(jti)
        return entry and entry == 'true'

    @staticmethod
    async def revoke_token(authorizer: AuthJWT, token_type: TokenType = TokenType.ACCESS) -> bool:
        authorizer.jwt_required()
        jti = authorizer.get_raw_jwt()['jti']
        time_to_live = timedelta(
            seconds=utils_settings.ACCESS_TOKEN_EXPIRE_SECONDS) if token_type is TokenType.ACCESS else timedelta(
            seconds=utils_settings.REFRESH_TOKEN_EXPIRE_SECONDS)

        await RedisUtils.set_redis(jti, 'true', time_to_live)  # Store until token expires

        authorizer.unset_jwt_cookies()

        return True

    @staticmethod
    def set_access_token(user: ActiveAuditor, authorizer: AuthJWT):
        subject = user.id
        access_token_expires = timedelta(seconds=utils_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        refresh_token_expires = timedelta(seconds=utils_settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        add_claims = {'ip': '127.0.0.1', 'user_type': user.user_type}  # TODO populate with user roles
        access_token = authorizer.create_access_token(subject=subject, expires_time=access_token_expires,
            user_claims=add_claims)
        refresh_token = authorizer.create_refresh_token(subject=subject, expires_time=refresh_token_expires,
            user_claims=add_claims)

        # Set the JWT and CSRF double submit cookies in the response
        try:
            authorizer.set_access_cookies(access_token)
            authorizer.set_refresh_cookies(refresh_token)

            return True
        except Exception as exc:
            print(exc)
            return False

    @staticmethod
    async def refresh_access_token(authorizer: AuthJWT) -> bool :
        authorizer.jwt_refresh_token_required()
        current_user = authorizer.get_jwt_subject()

        await JwtAuthUtils.revoke_token(authorizer)

        access_token_expires = timedelta(seconds=utils_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        add_claims = {'ip': '127.0.0.1'}  # TODO populate with user roles

        access_token = authorizer.create_access_token(subject=current_user, expires_time=access_token_expires,
            user_claims=add_claims)

        # Set the JWT and CSRF double submit cookies in the response
        try:
            authorizer.set_access_cookies(access_token)
            return True
        except Exception as exc:
            print(exc)
            raise

    @staticmethod
    async def login_success(user_json: dict, authorizer: AuthJWT):
        user_id = Utils.remove_dash(user_json['id'])
        user_json['id'] = user_id
        active_auditor: ActiveAuditor = await ActiveAuditorService.login(user_id, user_json)
        JwtAuthUtils.set_access_token(active_auditor, authorizer)
        user_json["bvn"] = None
        return LoginSuccessDto(**user_json)

    @staticmethod
    async def access_token_protected(token: str = Depends(oauth2_scheme), authorizer: AuthJWT = Depends()):
        authorizer.jwt_required()
        return authorizer

    @staticmethod
    def generate_pkce() -> tuple[str, str, str]:
        code_verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')

        state  = secrets.token_urlsafe(16)

        return code_challenge, code_verifier, state
