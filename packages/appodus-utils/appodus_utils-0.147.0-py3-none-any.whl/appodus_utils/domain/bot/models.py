from typing import Optional

from appodus_utils import BaseEntity, PageRequest, BaseQueryDto, Object
from pydantic import Field
from sqlalchemy import Column, String, Boolean, TEXT


class ChatBot(BaseEntity):
    __tablename__ = 'chatbots'
    client_id = Column(String(60), nullable=False)
    project = Column(String(60), nullable=False)
    bot_name = Column(String(60), nullable=False)
    bot_persona = Column(TEXT(), nullable=False)
    bot_intro_message = Column(TEXT(), nullable=False)
    bot_tone_and_voice = Column(TEXT(), nullable=False)
    restrict_to_provided_info = Column(Boolean, nullable=False)
    your_brand_name = Column(String(60), nullable=False)
    about_your_brand = Column(TEXT(), nullable=False)


class BotMessageBaseDto(Object):
    # client_id: str = Field(..., title="Client ID", description="The Client API ID")
    message: str = Field(..., title="Message", description="The chat message")


class BotChatOnceDto(BotMessageBaseDto):
    context: str = Field(..., title="Context", description="The context you would want the chatbot to respond from")


class BotChatDto(BotMessageBaseDto):
    position: int = Field(..., title="Position", description="The chronological order of the chat messages")
    project: str = Field(..., title="Project", description="The project that owns the chatbot")


class BotTrainDto(Object):
    bot_name: str = Field(..., title="Bot name", description="Give your bot a name. This name brands the chat ui also.")
    bot_persona: str = Field(..., title="Bot persona", description="Help your bot understand who she is", examples=[
        "You are a helpful, smart assistant designed to support users of the client's product."])
    bot_intro_message: str = Field(..., title="Bot Intro Message",
                                   description="With what message should I start the chat", examples=[])
    bot_tone_and_voice: str = Field(..., title="Bot tone and voice", description="How should your bot sound",
                                    examples=['"friendly": "friendly, conversational, and supportive"',
                                              '"formal": "professional, clear, and concise"',
                                              '"technical": "precise, structured, and technical"',
                                              '"casual": "laid-back, informal, and human-like"',
                                              '"sales": "persuasive, energetic, and conversion-focused"',
                                              ]
                                    )
    restrict_to_provided_info: bool = Field(True, title="Restrict to provided information",
                                            description="Restrict bot's response to only your provided information")
    your_brand_name: str = Field(..., title="Your brand name", description="State your name",
                                 examples=["Google", "Facebook", "appodus", "OpenAi"])
    about_your_brand: str = Field(..., title="About your brand",
                                  description="Talk about your brand in the clearest way possible")


class CreateChatBotDto(BotTrainDto):
    project: str = Field(..., title="Project", description="The project that owns the chatbot")


class _CreateChatBotDto(CreateChatBotDto):
    client_id: str = Field(..., title="Client ID", description="The Client API ID")


class UpdateChatBotDto(Object):
    bot_name: Optional[str] = None
    bot_persona: Optional[str] = None
    bot_intro_message: Optional[str] = None
    bot_tone_and_voice: Optional[str] = None
    restrict_to_provided_info: Optional[bool] = None
    your_brand_name: Optional[str] = None
    about_your_brand: Optional[str] = None


class SearchChatBotDto(PageRequest, BaseQueryDto):
    bot_name: Optional[str] = None


class QueryChatBotDto(BaseQueryDto, _CreateChatBotDto):
    pass

class ChatResponseDto(Object):
    answer: str
    session_id: Optional[str] = None


"""

documents
Guardrails / boundaries
Target audience (e.g., customers, team, investors)


Train
- client_id
- project
- bot_name
- bot_description
- bot_intro_message
- bot_tone_and_voice
- target_audience
- about_your_brand

Chat
- client_id
- domain
- session_id
- message

Query
- client_id
- message
- context
"""
