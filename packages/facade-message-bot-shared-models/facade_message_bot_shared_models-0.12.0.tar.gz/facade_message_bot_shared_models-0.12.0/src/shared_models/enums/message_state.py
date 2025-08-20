from enum import StrEnum


class MessageState(StrEnum):
    """MessageState Enum

    Args:
        - PENDING_AUTO_MODERATION: Message is awaiting automatic moderation.
        - PENDING_MANUAL_MODERATION: Message is awaiting manual moderation.
        - PENDING_MEDIA_FACADE_MODERATION: Message is awaiting media facade moderation.
        - REJECTED: Message has been rejected.
        - APPROVED: Message has been approved.
        - CANCELED: Message has been canceled.
        - SHOWN: Message has been shown to the user.
    """

    PENDING_AUTO_MODERATION = "pending_auto_moderation"
    PENDING_MANUAL_MODERATION = "pending_manual_moderation"
    PENDING_MEDIA_FACADE_MODERATION = "pending_media_facade_moderation"
    REJECTED = "rejected"
    APPROVED = "approved"
    CANCELED = "canceled"
    SHOWN = "shown"

    def __str__(self) -> str:
        return self.value
