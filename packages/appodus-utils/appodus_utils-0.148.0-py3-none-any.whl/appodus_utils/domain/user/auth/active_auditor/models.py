from datetime import datetime
from typing import Optional, List

from appodus_utils import Object

from appodus_utils.domain.user.models import UserPersona


class ActiveAuditor(Object):
    id: str
    dob: Optional[datetime] = None
    firstname: str
    lastname: str
    fullname: str
    phone: Optional[str] = None
    phone_ext: Optional[str] = None
    email: str
    user_type: str
    personas: Optional[List[UserPersona]] = None
    last_active_date: Optional[datetime] = None

    has_profile_picture: Optional[bool] = None
    has_selfie_picture: Optional[bool] = None
    phone_validated: Optional[bool] = None
    email_validated: Optional[bool] = None
    languages: Optional[List[str]] = None
    bvn_validated: Optional[bool] = None
    identity_validated: Optional[bool] = None
    address_validated: Optional[bool] = None
    driver_id: Optional[str] = None
    wallet_id: Optional[str] = None
    profile_id: Optional[str] = None
    host_id: Optional[str] = None
    escrow_id: Optional[str] = None
    lien_id: Optional[str] = None
    inbox_id: Optional[str] = None
    # token: Optional[str] = None
