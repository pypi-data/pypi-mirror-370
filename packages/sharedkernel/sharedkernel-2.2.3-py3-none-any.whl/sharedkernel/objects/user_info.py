from pydantic import BaseModel   

from contextvars import ContextVar

class UserInfo(BaseModel):
    nameid: str
    unique_name: str | None = None
    email: str | None = None
    role: str | None = None


current_user_info: ContextVar[UserInfo] = ContextVar("current_user_info")

