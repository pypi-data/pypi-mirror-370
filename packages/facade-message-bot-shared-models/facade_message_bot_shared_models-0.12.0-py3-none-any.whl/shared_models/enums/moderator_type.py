from enum import StrEnum


class ModeratorType(StrEnum):
    """ModeratorType Enum

    Args:
        - AUTO: Automatic moderation
        - MANUAL: Manual moderation
        - MEDIA_FACADE: Media facade moderation
    """

    AUTO = "auto"
    MANUAL = "manual"
    MEDIA_FACADE = "media_facade"

    def __str__(self) -> str:
        return self.value
