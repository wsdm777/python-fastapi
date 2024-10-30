from datetime import datetime
from pydantic import BaseModel


class PostRead(BaseModel):
    id: int
    user_id: int
    topic: str
    content: str | None
    created_at: datetime