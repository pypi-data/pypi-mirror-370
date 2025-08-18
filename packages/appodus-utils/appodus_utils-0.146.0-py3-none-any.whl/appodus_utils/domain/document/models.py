import enum
import json
from typing import Optional, List

from fastapi import Form
from pydantic import Field

from appodus_utils import Object


class DocumentAccessScope(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    INTERNAL = "internal"


class DocumentMetadata(Object):
    tags: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    description: Optional[str] = None


class CreateDocumentDto(Object):
    store_key: str
    store_bucket: Optional[str] = None
    access_scope: DocumentAccessScope = DocumentAccessScope.PRIVATE
    extras: Optional[DocumentMetadata] = Field(default_factory=DocumentMetadata)

    @classmethod
    def as_form(
        cls,
        store_key: str = Form(...),
        access_scope: DocumentAccessScope = Form(...),
        store_bucket: str = Form(None),
        tags: Optional[List[str]] = Form(None), # comma-separated string
        owner: Optional[str] = Form(None),
        description: Optional[str] = Form(None)
    ) -> "CreateDocumentDto":

        return cls(
            store_bucket=store_bucket,
            store_key=store_key,
            access_scope=access_scope,
            extras= DocumentMetadata(
                tags=cls.parse_tags(tags),
                owner=owner,
                description=description
            )
        )

    @classmethod
    def parse_tags(cls, raw_tags: List[str] = None) -> List[str]:
        if not raw_tags or not raw_tags[0]:
            return []

        value = raw_tags[0].strip()

        # Try parsing as JSON string (e.g., '["tag1", "tag2"]')
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [tag.strip() for tag in parsed if isinstance(tag, str)]
        except json.JSONDecodeError:
            pass

        # Fallback: parse as comma-separated string (e.g., 'tag1, tag2')
        return [tag.strip() for tag in value.split(",") if tag.strip()]


class FileDto(Object):
    url: str
    document_id: str
