import enum
from datetime import datetime, date
from typing import Optional

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto, Object, Utils
from pydantic import Field
from sqlalchemy import Column, String, DateTime, Text, Date, Boolean


class UserPersona(str, enum.Enum):
    GUEST = 'GUEST'
    SELLER = 'SELLER'
    BUYER = 'BUYER'

class KYCAgent(str, enum.Enum):
    EMAIL = 'EMAIL'
    PHONE = 'PHONE'
    ADDRESS = 'ADDRESS'
    BVN = 'BVN'
    IDENTITY = 'IDENTITY'
    PROFILE_PICTURE = 'PROFILE_PICTURE'

class UserStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    LOCKED = 'LOCKED'
    DEACTIVATED = 'DEACTIVATED'


class UserType(str, enum.Enum):
    ADMIN = 'A'
    USER = 'U'


class Gender(str, enum.Enum):
    MALE = 'M'
    FEMALE = 'F'
    OTHERS = 'O'


class Roles(str, enum.Enum):
    SUPER_USER = 'SUPER_USER'
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    ACCOUNTANT = 'ACCOUNTANT'
    SURVEYOR = 'SURVEYOR'
    LAWYER = 'LAWYER'


class User(BaseEntity):
    __tablename__ = 'users'
    email = Column(String(60), nullable=False)
    phone = Column(String(25), nullable=True)
    phone_ext = Column(String(6), nullable=True)
    password = Column(String(512), nullable=True)
    password_last_updated = Column(DateTime(), nullable=True)
    firstname = Column(String(30), nullable=False)
    middle_name = Column(String(30), nullable=True)
    lastname = Column(String(30), nullable=False)
    user_type = Column(String(2), nullable=False)
    status = Column(String(12), nullable=False)
    dob = Column(Date(), nullable=True)
    gender = Column(String(2), nullable=True)
    last_active_date = Column(DateTime(), nullable=True)
    notes = Column(Text, nullable=True)

    profile_picture_doc_id = Column(String(36), nullable=True, comment="")
    selfie_picture_doc_id = Column(String(36), nullable=True, comment="")

    bvn = Column(String(40), nullable=True)
    bvn_validated = Column(Boolean, nullable=False, default=False)
    phone_validated = Column(Boolean, nullable=False, default=False)
    email_validated = Column(Boolean, nullable=False, default=False)
    identity_validated = Column(Boolean, nullable=False, default=False)
    address_id = Column(String(36), nullable=True)
    address_validated = Column(Boolean, nullable=False, default=False)
    selfie_validated = Column(Boolean, nullable=False, default=False)


class UserBaseDto(Object):
    gender: Optional[Gender] = None


class CreateUserDto(UserBaseDto):
    otp: str
    email: str
    phone: Optional[str] = None
    phone_ext: Optional[str] = None
    password: str
    firstname: str = Field(..., min_length=2, max_length=30)
    lastname: str = Field(..., min_length=2, max_length=30)

class CreateUserOptionalPasswordDto(CreateUserDto):
    password: Optional[str] = None

class _CreateUserDto(CreateUserDto):
    user_type: UserType = UserType.USER
    status: UserStatus = UserStatus.INACTIVE
    password: Optional[str] = None
    # password_last_updated: datetime = Utils.datetime_now_to_db()

    bvn_validated: bool = False
    phone_validated: bool = False
    email_validated: bool = False
    identity_validated: bool = False
    address_validated: bool = False


class _UpdateUserDto(Object):
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    last_active_date: Optional[datetime] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    phone_ext: Optional[str] = None
    password: Optional[str] = None
    password_last_updated: Optional[datetime] = None
    status: Optional[UserStatus] = None
    firstname: Optional[str] = None
    middle_name: Optional[str] = None
    lastname: Optional[str] = None
    notes: Optional[str] = None

    profile_picture_doc_id: Optional[str] = None
    selfie_picture_doc_id: Optional[str] = None

    bvn: Optional[str] = None
    bvn_validated: Optional[bool] = None
    phone_validated: Optional[bool] = None
    email_validated: Optional[bool] = None
    identity_validated: Optional[bool] = None
    address_id: Optional[str]  = None
    address_validated: Optional[bool] = None


class UpdateUserDto(UserBaseDto):
    pass


class UpdateNameDto(Object):
    firstname: str
    middle_name: str
    lastname: str


class SearchUserDto(PageRequest, BaseQueryDto, _UpdateUserDto):
    user_type: Optional[UserType] = None


class QueryUserDto(UserBaseDto, BaseQueryDto, _UpdateUserDto):
    def __init__(self, **kwargs):
        kwargs.setdefault('fullname',
                          get_fullname(kwargs.get('firstname'), kwargs.get('middle_name'), kwargs.get('lastname')))
        kwargs["password"] = ""  # Hide password
        super().__init__(**kwargs)

    fullname: Optional[str] = None
    user_type: Optional[UserType] = None


def get_fullname(firstname: str, middle_name: str, lastname: str) -> str:
    return " ".join(part for part in [firstname, middle_name, lastname] if part)


class VerificationStatus(str, enum.Enum):
    PENDING = 'PENDING'
    CORRECTIONS_NEEDED = "corrections_needed"
    UNDER_REVIEW = "under_review"
    VERIFIED = 'VERIFIED'
    FAILED = 'FAILED'
