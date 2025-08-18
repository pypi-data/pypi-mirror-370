from typing import Optional

from appodus_utils import Object


class MessageResponse(Object):
    ai: str
    user: Optional[str] = None
