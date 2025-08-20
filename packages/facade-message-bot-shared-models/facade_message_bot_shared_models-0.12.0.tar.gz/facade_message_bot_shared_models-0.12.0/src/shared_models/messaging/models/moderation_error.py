from .error_response import ErrorResponse
from .message_input import MessageInput


class ModerationError(ErrorResponse, MessageInput):
    pass
