from datetime import datetime
from typing import Optional

from appodus_utils import Object, BaseEntity, BaseQueryDto, PageRequest, Utils
from sqlalchemy import Column, String, DateTime, Integer


class ChatSession(BaseEntity):
    __tablename__ = 'chat_sessions'
    client_id = Column(String(36), nullable=False)
    start_time = Column(DateTime(), nullable=False)
    duration = Column(Integer, nullable=False)
    user_firstname = Column(String(20), nullable=True)
    user_lastname = Column(String(20), nullable=True)
    user_email = Column(String(30), nullable=True)
    user_phone = Column(String(14), nullable=True)


class ChatSessionBaseDto(Object):
    pass


class CreateChatSessionDto(ChatSessionBaseDto):
    start_time: datetime = Utils.datetime_now_to_db()
    duration: int = 0


class _CreateChatSessionDto(CreateChatSessionDto):
    id: str
    client_id: str


class UpdateChatSessionDto(ChatSessionBaseDto):
    pass


class _UpdateChatSessionDto(Object):
    duration: Optional[int] = None
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None

class UpdateChatSessionUserDto(Object):
    user_firstname: Optional[str] = None
    user_lastname: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None



class QueryChatSessionDto(CreateChatSessionDto, BaseQueryDto):
    pass


class SearchChatSessionDto(PageRequest, BaseQueryDto):
    client_id: Optional[str] = None
