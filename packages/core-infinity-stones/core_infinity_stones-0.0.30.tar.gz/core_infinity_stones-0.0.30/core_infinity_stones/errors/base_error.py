from enum import StrEnum
from typing import Any, Optional
from pydantic import BaseModel
from typing_extensions import deprecated

class Severity(StrEnum):
    """Severity levels for errors and events."""

    CRITICAL = "CRITICAL"
    """Service-down, data loss, or security breaches. Immediate attention required"""

    HIGH = "HIGH"
    """Major functional issue that affects important workflows. Requires prompt resolution."""

    MEDIUM = "MEDIUM"
    """Degraded functionality or partial impact. Should be fixed soon."""

    LOW = "LOW"
    """Minor errors that don’t impact most users or core functionality."""

    INFO = "INFO"
    """Informational errors that don’t impact the app behavior (e.g. validation errors or user mistakes)."""


class LocalizedMessage(BaseModel):
    ar: str
    en: str


class HttpErrorPublicDetails(BaseModel):
    code: str
    status_code: int
    message: LocalizedMessage
    details: dict[Any, Any]


class HttpErrorDebugDetails(BaseModel):
    severity: Severity
    debug_code: str
    occurred_while: Optional[str]
    caused_by: Optional[Exception] = None
    debug_message: str
    debug_details: dict[Any, Any] = {}
    topic: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Exception: lambda e: str(e),
        }


class HttpError(Exception):
    def __init__(
        self,
        code: str,
        severity: Severity,
        status_code: int,
        message: LocalizedMessage,
        details: dict[Any, Any] = {},
        topic: Optional[str] = None,
        debug_code: Optional[str] = None,
        debug_message: Optional[str] = None,
        occurred_while: Optional[str] = None,
        debug_details: dict[Any, Any] = {},
        caused_by: Optional[Exception] = None,
    ) -> None:
        self.public_details = HttpErrorPublicDetails(
            code=code,
            status_code=status_code,
            message=message,
            details=details,
        )

        self.debug_details = HttpErrorDebugDetails(
            severity=severity,
            debug_code=debug_code or code,
            occurred_while=occurred_while,
            caused_by=caused_by,
            debug_message=debug_message or message.en,
            debug_details=debug_details,
            topic=topic,
        )


class UnexpectedError(HttpError):
    def __init__(
        self,
        severity: Severity = Severity.CRITICAL,
        topic: Optional[str] = None,
        debug_code: Optional[str] = None,
        debug_message: Optional[str] = None,
        occurred_while: Optional[str] = None,
        debug_details: dict[Any, Any] = {},
        caused_by: Optional[Exception] = None,
    ) -> None:
        super().__init__(
            status_code=500,
            severity=severity,
            code="UNEXPECTED_ERROR",
            message=LocalizedMessage(
                ar="حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقًا.",
                en="Something went wrong. Please try again later.",
            ),
            details={},
            topic=topic,
            debug_code=debug_code,
            debug_message=debug_message,
            occurred_while=occurred_while,
            debug_details=debug_details,
            caused_by=caused_by,
        )


# MARK: DEPRECATED


@deprecated("BaseError is deprecated. Use `HttpError` instead.")
class BaseError(Exception):
    def __init__(
        self,
        status_code: int,
        occurred_while: str,
        caused_by: Optional[Exception] = None,
        debug_description: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self.status_code = status_code
        self.occurrence_context = occurred_while
        self.original_error = caused_by
        self._debug_description = debug_description
        self._message = message

    @property
    def debug_description(self) -> str:
        debug_description = f"Error occurred while {self.occurrence_context}\n"

        if self._debug_description:
            debug_description += f"with message: {self._debug_description}\n"

        if self.original_error:
            debug_description += f"caused by: {self.original_error}"

        return debug_description

    @property
    def message(self) -> str:
        if self._message:
            return self._message
        return f"Something went wrong while {self.occurrence_context}"
