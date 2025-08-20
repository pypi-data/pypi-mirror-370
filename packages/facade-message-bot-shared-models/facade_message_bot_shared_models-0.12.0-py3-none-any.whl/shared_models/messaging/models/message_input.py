from pydantic import BaseModel, Field
from typing import Annotated
from .message import Message


class MessageInput(BaseModel):
    message: Annotated[
        Message, Field(..., description="The message associated with the notification.")
    ]
