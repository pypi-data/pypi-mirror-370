import ast
import json
import re
from operator import attrgetter
from typing import Dict, List, Optional, Set, ClassVar, TypeVar, Type, Tuple

import cachetools

from appodus_utils.exception.exceptions import ValidationException
from pydantic import Field, PrivateAttr, field_validator, ConfigDict

from appodus_utils import Object, Utils
from appodus_utils.integrations.messaging.models import MessagePriority

T = TypeVar("T", bound="MessagingConfig")

class MessagingConfig(Object):
    """Immutable messaging configuration with validated fields."""

    _subject_cache = cachetools.LRUCache(maxsize=54)

    # Public fields (immutable by convention)
    from_email: str
    from_name: str = Field(..., min_length=1, max_length=100)
    sms_ttl: int = Field(..., gt=60, le=86400)
    sms_sender_id: str = Field(..., min_length=1, max_length=11)
    headers: Dict[str, str] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    sandbox_mode: bool = False
    brand_name: str
    otp_token_expire_mins: str
    categories: Optional[List[str]] = Field(default_factory=list)
    subjects: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of subject keys to email subject templates"
    )

    # Private attributes
    _normalized_subjects: Tuple[Tuple[str, str], ...] = PrivateAttr()

    def normalize_subjects(self):
        normalized_subjects = {
            k.replace('_subject', '').lower(): v
            for k, v in self.subjects.items()
        }
        self._normalized_subjects = tuple(sorted(normalized_subjects.items()))

    # Class-level constants
    _required_subjects: ClassVar[Set[str]] = {
        'otp',
        'account_activation',
        'account_deactivation',
        'email_verification',
        'login_diff_device_security_alert',
        'name_update_success',
        'new_feature_announcement',
        'new_user_email_verification',
        'new_user_welcome',
        'password_reset_request',
        'password_update_success',
        'phone_verification',
    }

    # Pydantic v2 config
    model_config = ConfigDict(
        frozen=True,  # Makes instances immutable
        extra='forbid',  # Prevents extra fields
        str_strip_whitespace=True,  # Auto-trim strings
    )

    @field_validator('from_name')
    @classmethod
    def validate_from_name(cls, v: str) -> str:
        if not re.match(r'^[\w\s\-\.]+$', v):
            raise ValueError("From name contains invalid characters")
        return v

    @field_validator('sms_sender_id')
    @classmethod
    def validate_sms_id(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValidationException(message="SMS SENDER ID allows only alphanumeric chars and spaces")
        return v

    @field_validator('subjects')
    @classmethod
    def validate_subjects(cls, v: Dict[str, str]) -> Dict[str, str]:
        normalized_keys = {k.replace('_subject', '').lower() for k in v}
        missing = cls._required_subjects - normalized_keys
        if missing:
            raise ValueError(f"Missing required subjects: {', '.join(sorted(missing))}")

        for key, value in v.items():
            if len(value) > 150:
                raise ValueError(f"Subject '{key}' exceeds 150 character limit")
        return v

    # --- Init hook ---
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.normalize_subjects()

    # --- Cached subject lookup ---
    @cachetools.cachedmethod(attrgetter('_subject_cache'), key=lambda self, key: key)
    def get_subject(self, key: str) -> str:
        """O(1) subject lookup."""
        normalized = key.replace('_subject', '').lower()
        if subject := dict(self._normalized_subjects).get(normalized):
            return subject
        raise KeyError(f"Invalid subject key: {key}")

    # --- Constructor from app settings ---
    @classmethod
    def from_settings(cls: Type[T]) -> T:
        """Preferred constructor from settings."""
        EMAIL_FROM_ADDRESS = Utils.get_from_env_fail_if_not_exists("EMAIL_FROM_ADDRESS")
        EMAIL_FROM_NAME = Utils.get_from_env_fail_if_not_exists("EMAIL_FROM_NAME")
        SMS_TTL = Utils.get_from_env_fail_if_not_exists("SMS_TTL")
        SMS_SENDER_ID = Utils.get_from_env_fail_if_not_exists("SMS_SENDER_ID")
        MESSAGING_HEADERS = Utils.get_from_env("MESSAGING_HEADERS")
        MESSAGING_PRIORITY = Utils.get_from_env("MESSAGING_PRIORITY")
        MESSAGING_SANDBOX_MODE = Utils.get_from_env("MESSAGING_SANDBOX_MODE")
        MESSAGING_CATEGORIES = Utils.get_from_env("MESSAGING_CATEGORIES")
        EMAIL_SUBJECTS = Utils.get_from_env("EMAIL_SUBJECTS")
        MESSAGING_BRAND_NAME = Utils.get_from_env_fail_if_not_exists("MESSAGING_BRAND_NAME")
        OTP_TOKEN_EXPIRE_SECONDS = Utils.get_from_env_fail_if_not_exists("OTP_TOKEN_EXPIRE_SECONDS")


        return cls(
            from_email=EMAIL_FROM_ADDRESS,
            from_name=EMAIL_FROM_NAME,
            sms_ttl=int(SMS_TTL) if SMS_TTL else 25000,
            sms_sender_id=SMS_SENDER_ID,
            headers=ast.literal_eval(MESSAGING_HEADERS) if MESSAGING_HEADERS else {},
            priority=MESSAGING_PRIORITY or 2,
            sandbox_mode=bool(MESSAGING_SANDBOX_MODE) if MESSAGING_SANDBOX_MODE else False,
            categories=json.loads(MESSAGING_CATEGORIES) if MESSAGING_CATEGORIES else [],
            subjects=ast.literal_eval(EMAIL_SUBJECTS) if EMAIL_SUBJECTS else {},
            brand_name = MESSAGING_BRAND_NAME,
            otp_token_expire_mins = f"{(int(OTP_TOKEN_EXPIRE_SECONDS) / 60)}" if OTP_TOKEN_EXPIRE_SECONDS else "5"

        )
