import random
from datetime import datetime, timezone
from logging import Logger as NativeLogger
import traceback
from typing import Any, Callable, Optional

from core_infinity_stones.errors.base_error import HttpError
from core_infinity_stones.logging.native_logger import json_event_logger
from core_infinity_stones.logging.schemas import (
    ErrorEvent,
    Event,
    EventLevel,
    EventWithTracesDetails,
    RequestDetails,
    TracingDetails,
)


class Logger:
    def __init__(
        self,
        service_name: str,
        tracing_details_resolver: Callable[[], TracingDetails],
        logger: NativeLogger = json_event_logger,
        event_codes_to_sampling_percentages_map: Optional[dict[str, int]] = None,
        request_details: Optional[RequestDetails] = None,
    ):
        """
        Initialize the Logger instance.

        Args:
            service_name (str): The name of the service.

            tracing_details_resolver (Callable[[], TracingDetails]): A callable that returns tracing details
                for the current request or context.

            logger (NativeLogger): The logger instance to use for logging events.

            event_codes_to_sampling_percentages_map (Optional[dict[str, int]]): A mapping of event
                codes to their sampling percentages.
                This is a dictionary where keys are event codes and values are integers between 0 and 100,
                representing the probability of logging the specified event.
                If None, all events will be logged with 100% sampling.
                If an event code is not present in the map, it will default to 100% sampling.

            request_details (Optional[RequestDetails]): Details about the request,
              such as path, method, and query parameters.
        """
        self.service_name = service_name
        self.tracing_details_resolver = tracing_details_resolver
        self.logger = logger
        self.request_details = request_details
        self.event_codes_to_sampling_percentages_map = (
            event_codes_to_sampling_percentages_map
        )

    def info(self, event: Event) -> None:
        if not self._should_log_based_on_sampling_percentage(event.code):
            return

        sampling_percentage = (
            self.event_codes_to_sampling_percentages_map.get(event.code, 100)
            if self.event_codes_to_sampling_percentages_map
            else 100
        )

        tracing_details = self.tracing_details_resolver()

        event_with_tracing_details = EventWithTracesDetails.from_event(
            event,
            tracing_details,
            level=EventLevel.INFO,
            service=self.service_name,
            sampling_percentage=sampling_percentage,
            request_details=self.request_details,
        )

        self.logger.info(event.message, extra={"event": event_with_tracing_details})

    def warning(self, event: Event) -> None:
        if not self._should_log_based_on_sampling_percentage(event.code):
            return

        sampling_percentage = (
            self.event_codes_to_sampling_percentages_map.get(event.code, 100)
            if self.event_codes_to_sampling_percentages_map
            else 100
        )

        tracing_details = self.tracing_details_resolver()

        event_with_tracing_details = EventWithTracesDetails.from_event(
            event,
            tracing_details,
            level=EventLevel.WARNING,
            service=self.service_name,
            sampling_percentage=sampling_percentage,
            request_details=self.request_details,
        )

        self.logger.warning(event.message, extra={"event": event_with_tracing_details})

    def error(self, error: HttpError) -> None:
        event_code = error.debug_details.debug_code

        if not self._should_log_based_on_sampling_percentage(event_code):
            return

        error_event = self._format_error(error)

        self.logger.error(
            error.debug_details.debug_message, extra={"event": error_event}
        )

    def _format_error(self, error: Optional[BaseException]) -> Optional[dict[str, Any]]:
        """
        Formats the error into a string representation.
        """
        if error is None:
            return None

        if isinstance(error, HttpError):
            tracing_details = self.tracing_details_resolver()
            event_code = error.debug_details.debug_code

            original_error_details = self._format_error(error.debug_details.caused_by)

            sampling_percentage = (
                self.event_codes_to_sampling_percentages_map.get(event_code, 100)
                if self.event_codes_to_sampling_percentages_map
                else 100
            )

            return ErrorEvent(
                trace_id=tracing_details.trace_id,
                span_id=tracing_details.span_id,
                code=event_code,
                topic=error.debug_details.topic,
                level=EventLevel.ERROR,
                service=self.service_name,
                path=self.request_details.path if self.request_details else None,
                method=self.request_details.method if self.request_details else None,
                query_params=self.request_details.query_params if self.request_details else None,
                user_agent=self.request_details.user_agent if self.request_details else None,
                message=error.debug_details.debug_message,
                details=error.debug_details.debug_details,
                severity=error.debug_details.severity,
                occurred_while=error.debug_details.occurred_while,
                caused_by=original_error_details,
                status_code=error.public_details.status_code,
                public_code=error.public_details.code,
                public_message=error.public_details.message,
                public_details=error.public_details.details,
                sampling_percentage=sampling_percentage,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
            ).model_dump(mode="json")

        return {
            "type": type(error).__name__,
            "message": str(error),
            "stack_trace": traceback.format_exception(
                type(error), error, error.__traceback__
            ),
        }


    def _should_log_based_on_sampling_percentage(self, event_code: str) -> bool:
        """
        Determines whether an event should be logged based on its code and the configured sampling percentages.
        """

        if not self.event_codes_to_sampling_percentages_map:
            return True

        sampling_percentage = self.event_codes_to_sampling_percentages_map.get(event_code, 100)

        if sampling_percentage <= 0:
            return False

        if sampling_percentage >= 100:
            return True

        return random.randint(0, 100) < sampling_percentage