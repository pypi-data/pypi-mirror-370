import enum

from appodus_utils import Object
from appodus_utils.domain.user.auth.models import SocialAuthOperationType


class SocialAuthPlatform(str, enum.Enum):
    APPLE = "apple"
    FACEBOOK = "facebook"
    GOOGLE = "google"


class OAuthRequestStoredState(Object):
    code_verifier: str
    operation_type: SocialAuthOperationType
    redirect_uri: str
    frontend_origin: str
