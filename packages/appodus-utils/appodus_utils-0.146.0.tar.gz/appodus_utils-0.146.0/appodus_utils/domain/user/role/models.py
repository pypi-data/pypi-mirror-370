import enum
from typing import Optional

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto
from appodus_utils import Object
from sqlalchemy import Column, String


class Role(str, enum.Enum):
    SUPER_USER = "SUPER_USER" # Account owner
    ADMIN = "ADMIN" # In a company
    ACCOUNTANT = "ACCOUNTANT" # In a company
    LEGAL = "LEGAL" # In a company
    AGENT = "AGENT" # In a company
    VIEWER = "VIEWER" # In a company

class Currency(BaseEntity):
    __tablename__ = 'currencies'
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    permissions = Column(String, nullable=False)
    is_active = Column(String(12), nullable=False)


class CurrencyBaseDto(Object):
    name: str
    code: str
    country_code: str


class CreateCurrencyDto(CurrencyBaseDto):
    is_active: bool = True


class UpdateCurrencyDto(CurrencyBaseDto):
    name: Optional[str]
    code: Optional[str]
    country_code: Optional[str]


class _UpdateCurrencyDto(Object):
    is_active: Optional[bool]


class SearchCurrencyDto(PageRequest, BaseQueryDto):
    name: Optional[str] = None
    code: Optional[str] = None
    country_code: Optional[str] = None
    is_active: Optional[bool] = None


class QueryCurrencyDto(CurrencyBaseDto, BaseQueryDto):
    is_active: Optional[bool]
