from pydantic import BaseModel


class Event(BaseModel):
    file_name: str
    event_type: str
    response_content: str
    identifier: str
