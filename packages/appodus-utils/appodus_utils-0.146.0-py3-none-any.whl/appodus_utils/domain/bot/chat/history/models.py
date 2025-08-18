from typing import Optional

from appodus_utils import Object, BaseEntity, BaseQueryDto, PageRequest
from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.ext.mutable import MutableDict

from appodus_utils.integrations.ai_llm.models import MessageResponse


class ChatHistory(BaseEntity):
    __tablename__ = 'chat_histories'
    session_id = Column(String(128), nullable=False)
    chat = Column(MutableDict.as_mutable(JSON), nullable=False)
    position = Column(Integer, nullable=False)


class ChatHistoryBaseDto(Object):
    chat: MessageResponse


class CreateChatHistoryDto(ChatHistoryBaseDto):
    session_id: str
    position: int


class UpdateChatHistoryDto(ChatHistoryBaseDto):
    pass


class QueryChatHistoryDto(CreateChatHistoryDto, BaseQueryDto):
    pass

class ChatResponseDto(Object):
    id: str
    response_message: str


class SearchChatHistoryDto(PageRequest, BaseQueryDto):
    session_id: Optional[str] = None
    position: Optional[int] = None
    order_by: str = "position desc"
