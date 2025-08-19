import enum
from typing import Optional

from pydantic import Field

from appodus_utils import Object, Utils
from appodus_utils.domain.user.models import QueryUserDto


class SocialAuthOperationType(str, enum.Enum):
    LOGIN = "login"
    SIGNUP = "signup"

class EmailLoginRequest(Object):
    username: str
    password: str


class PasswordResetRequest(Object):
    email: str

class EmailValidationRequest(Object):
    email: str


class PasswordResetConfirm(Object):
    token: str
    new_password: str


class ChangePasswordDto(Object):
    old_password: str
    new_password: str

class SocialAuthResponseType(str, enum.Enum):
    SOCIALAUTH_EXISTS = "SOCIALAUTH_EXISTS"
    SOCIALAUTH_NOTFOUND = "SOCIALAUTH_NOTFOUND"
    SOCIALAUTH_SUCCEEDED = "SOCIALAUTH_SUCCEEDED"


class SocialLoginUserInfo(Object):
    id: Optional[str] = None
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    exp: Optional[int] = 0
    otp: str = Field(default=Utils.random_str(8), description="Token used for email verification during user creation")
    operation_type: Optional[SocialAuthOperationType] = Field(None, description="Used to distinguish between a login/signup operation")
    frontend_origin: str
    response_code: Optional[SocialAuthResponseType] = SocialAuthResponseType.SOCIALAUTH_SUCCEEDED
    response_message: Optional[str] = "Auth operation succeeded"

class OAuthCallbackRequest(Object):
    code: str
    code_verifier: str
    operation_type: SocialAuthOperationType
    redirect_uri: str
    frontend_origin: str


class Token(Object):
    access_token: str
    refresh_token: str
    token_type: str


class TokenType(str, enum.Enum):
    ACCESS = 'ACCESS'
    REFRESH = 'REFRESH'


class Role(str, enum.Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    SELLER = 'SELLER'
    BUYER = 'BUYER'
    AGENT = 'AGENT'


class LoginSuccessDto(QueryUserDto):
    pass
