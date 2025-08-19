from sciop_cli.exceptions import SciopException


class QuestError(SciopException):
    """Generic parent class for all quest-related errors"""


class QuestUploadError(SciopException):
    """Parent exception for quest upload errors"""


class QuestValidationError(QuestError, ValueError):
    """Error emitted when a quest is invalid for the attempted action"""


class QuestInvalidUploadError(QuestUploadError, QuestValidationError):
    """A quest could not be uploaded because it was invalid or incomplete!"""
