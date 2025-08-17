from pydantic import BaseModel, Field
from datetime import datetime


class BaseDocument(BaseModel):
    id: str | None = None
    is_deleted: bool | None = False
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(default_factory=datetime.now)


class BaseAuditDocument(BaseDocument):
    pass
