from datetime import datetime
from pydantic import BaseModel


class QAGradio(BaseModel):
    question: str
    answer: str
    history: str
    exe_datetime: datetime
