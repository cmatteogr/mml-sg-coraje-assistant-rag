from datetime import datetime
from pydantic import BaseModel


class UserDiscord(BaseModel):
    id_discord: int
    name: str


class QADiscord(BaseModel):
    user_id: int
    question: str
    answer: str
    history: str
    exe_datetime: datetime
