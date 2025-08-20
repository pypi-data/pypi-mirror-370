from .message_input import MessageInput
from typing import Annotated, Optional
from pydantic import Field


class MessageShown(MessageInput):
    photo_base64: Annotated[
        Optional[str],
        Field(None, description="Base64 encoded photo, if any"),
    ] = None
