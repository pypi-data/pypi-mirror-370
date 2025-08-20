from enum import StrEnum


class ModerationResult(StrEnum):
    """ModerationResult Enum

    Args:
        - REJECTED: Message is rejected.
        - APPROVED: Message is approved.
    """

    REJECTED = "rejected"
    APPROVED = "approved"

    def __str__(self) -> str:
        return self.value
