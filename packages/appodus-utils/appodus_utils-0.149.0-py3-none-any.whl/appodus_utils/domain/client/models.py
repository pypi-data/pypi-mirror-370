from datetime import datetime
from typing import List, Optional

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto, Object, Utils
from pydantic import Field
from sqlalchemy import Column, String, JSON, Boolean, Integer, DateTime, TEXT
from sqlalchemy.ext.mutable import MutableDict


class Client(BaseEntity):
    __tablename__ = 'clients'
    name = Column(String(20), nullable=False)
    description = Column(TEXT, nullable=False)
    client_secret = Column(String(212), nullable=False)
    access_rules = Column(MutableDict.as_mutable(JSON), nullable=False)
    last_used = Column(DateTime(), nullable=False)
    usage_count = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)

class ClientAccessRuleDto(Object):
    allowed_ips: List[str] = Field(default_factory=list)
    allowed_domains: List[str] = Field(default_factory=list)
    allowed_origins: List[str] = Field(default_factory=list)

class ClientBaseDto(Object):
    access_rules: ClientAccessRuleDto = ClientAccessRuleDto()


class CreateClientDto(ClientBaseDto):
    name: str
    description: str


class _CreateClientDto(CreateClientDto):
    id: Optional[str] = None # Here just to allow us seed clients (appodus)
    client_secret: str
    last_used: datetime = Utils.datetime_now_to_db()
    usage_count: int = 0
    is_active: bool = True


class UpdateClientDto(ClientBaseDto):
    pass

class _UpdateClientDto(Object):
    name: Optional[str] = None
    description: Optional[str] = None


class SearchClientDto(PageRequest, BaseQueryDto):
    name: Optional[str] = None
    description: Optional[str] = None
    client_secret: Optional[str] = None
    is_active: Optional[bool] = None


class QueryClientDto(BaseQueryDto, CreateClientDto):
    def __init__(self, **kwargs):
        kwargs["client_secret"] = ""  # Hide client_secret
        super().__init__(**kwargs)
