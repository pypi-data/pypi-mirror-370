import importlib

try:
    importlib.import_module("faststream")
except ImportError:
    raise RuntimeError(
        "To use messaging, install package with [messaging] or [full] extra."
    )

from .models import (
    Message,
    MessageInput,
    MessageShown,
    ModerationResult,
    NoAvailableTime,
    AddToBlackList,
    ErrorResponse,
    ModerationError,
)
from .queues import (
    auto_moderator_queue,
    auto_moderator_dlx_queue,
    auto_moderator_black_list_dlx_queue,
    auto_moderator_black_list_queue,
    facade_message_moderator_queue,
    facade_message_moderator_dlx_queue,
    manual_moderator_queue,
    manual_moderator_dlx_queue,
    second_manual_moderator_queue,
    second_manual_moderator_dlx_queue,
    vision_notification_queue,
    vision_notification_dlx_queue,
    bot_moderate_response_queue,
    bot_moderate_response_dlx_queue,
    bot_message_shown_queue,
    bot_message_shown_dlx_queue,
)
from .exchanges import moderator_exchange, dlx_exchange, vision_exchange, bot_exchange


__all__ = [
    "Message",
    "MessageInput",
    "MessageShown",
    "ModerationResult",
    "NoAvailableTime",
    "AddToBlackList",
    "ErrorResponse",
    "ModerationError",
    "auto_moderator_queue",
    "auto_moderator_dlx_queue",
    "auto_moderator_black_list_dlx_queue",
    "auto_moderator_black_list_queue",
    "bot_exchange",
    "facade_message_moderator_queue",
    "facade_message_moderator_dlx_queue",
    "manual_moderator_queue",
    "manual_moderator_dlx_queue",
    "second_manual_moderator_queue",
    "second_manual_moderator_dlx_queue",
    "vision_notification_queue",
    "vision_notification_dlx_queue",
    "moderator_exchange",
    "dlx_exchange",
    "vision_exchange",
    "bot_moderate_response_queue",
    "bot_moderate_response_dlx_queue",
    "bot_message_shown_queue",
    "bot_message_shown_dlx_queue",
]
