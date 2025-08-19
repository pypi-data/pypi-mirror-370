from typing import Optional


from sqlalchemy import Column, String, Boolean

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto
from appodus_utils import Object


class Currency(BaseEntity):
    __tablename__ = 'currencies'
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)


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
