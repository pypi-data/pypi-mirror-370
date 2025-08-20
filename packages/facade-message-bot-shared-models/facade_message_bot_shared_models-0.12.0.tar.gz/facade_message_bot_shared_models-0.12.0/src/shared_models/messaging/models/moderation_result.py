from .message_input import MessageInput
from typing import Annotated, Optional
from pydantic import Field
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum


class ModerationResult(MessageInput):
    source: Annotated[
        ModeratorType,
        Field(
            ...,
            description="The type of moderation source (e.g., auto, manual, media facade).",
        ),
    ]
    result: Annotated[
        ModerationResultEnum,
        Field(
            ...,
            description="The result of the moderation action (e.g., rejected, approved).",
        ),
    ]
    reason: Annotated[
        Optional[str],
        Field(
            None,
            description="Optional reason for the moderation result, if applicable.",
        ),
    ] = None
