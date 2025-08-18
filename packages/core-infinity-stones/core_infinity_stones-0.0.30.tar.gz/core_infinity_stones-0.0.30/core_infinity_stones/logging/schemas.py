from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel

from core_infinity_stones.errors.base_error import LocalizedMessage, Severity


class TracingDetails(BaseModel):
    trace_id: str
    span_id: str

class RequestDetails(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    query_params: Optional[dict[str, str]] = None
    user_agent: Optional[str] = None

class EventLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Event(BaseModel):
    code: str
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    topic: Optional[str] = None


class EventWithTracesDetails(BaseModel):
    trace_id: str
    span_id: str
    level: EventLevel
    service: str
    path: Optional[str] = None
    method: Optional[str] = None
    query_params: Optional[dict[str, Any]] = None
    user_agent: Optional[str] = None
    code: str
    topic: Optional[str] = None
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    sampling_percentage: int
    timestamp: str

    @classmethod
    def from_event(
        cls,
        event: Event,
        tracing_details: TracingDetails,
        level: EventLevel,
        service: str,
        sampling_percentage: int,
        request_details: Optional[RequestDetails] = None,
    ) -> "EventWithTracesDetails":
        return EventWithTracesDetails(
            trace_id=tracing_details.trace_id,
            span_id=tracing_details.span_id,
            level=level,
            service=service,
            path=request_details.path if request_details else None,
            method=request_details.method if request_details else None,
            query_params=request_details.query_params if request_details else None,
            user_agent=request_details.user_agent if request_details else None,
            code=event.code,
            topic=event.topic,
            message=event.message,
            details=event.details,
            sampling_percentage=sampling_percentage,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )


class ErrorEvent(BaseModel):
    trace_id: str
    span_id: str
    level: EventLevel
    service: str
    path: Optional[str] = None
    method: Optional[str] = None
    query_params: Optional[dict[str, Any]] = None
    user_agent: Optional[str] = None
    severity: Severity
    code: str
    topic: Optional[str] = None
    message: str
    details: Optional[dict[str, Any]] = None
    occurred_while: Optional[str] = None
    caused_by: Optional[dict[str, Any]] = None
    status_code: int
    public_code: str
    public_message: LocalizedMessage
    public_details: Optional[dict[str, Any]] = None
    sampling_percentage: int
    timestamp: str