from datetime import datetime

from appodus_utils.db.models import Base, AutoRepr
from sqlalchemy import Column, String, LargeBinary, DateTime

from appodus_utils import Object, Utils


class KeyValue(Base, AutoRepr):
    __tablename__ = 'key_values'

    key = Column(String(128), primary_key=True,  unique=True, index=True, nullable=False)
    value = Column(LargeBinary, nullable=False)
    expires_at = Column(DateTime(), nullable=False)

    @property
    def is_expired(self):
        return self.expires_at <= Utils.datetime_now_to_db()


class UpsertKeyValue(Object):
    key: str
    value: bytes
    expires_at: datetime
