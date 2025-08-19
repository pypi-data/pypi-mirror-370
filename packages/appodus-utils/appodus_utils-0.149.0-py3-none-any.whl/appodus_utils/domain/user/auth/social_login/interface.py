from abc import ABC, abstractmethod

from starlette.requests import Request

from appodus_utils.domain.user.auth.models import SocialAuthOperationType, OAuthCallbackRequest, SocialLoginUserInfo
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform


class ISocialAuthProvider(ABC):
    @property
    @abstractmethod
    def platform(self) -> SocialAuthPlatform:
        pass

    @abstractmethod
    async def initialize(self, operation_type: SocialAuthOperationType, request: Request) -> dict:
        pass

    @abstractmethod
    async def verify(self, payload: OAuthCallbackRequest, request: Request) -> SocialLoginUserInfo:
        pass
