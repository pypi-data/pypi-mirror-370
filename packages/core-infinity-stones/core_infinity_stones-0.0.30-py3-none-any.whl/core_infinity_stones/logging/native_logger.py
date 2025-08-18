from datetime import datetime, timezone
import json
import logging

from pydantic import BaseModel


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "event") and isinstance(record.event, BaseModel):
            return record.event.model_dump_json()

        if hasattr(record, "event"):  # Event is a dictionary
            return json.dumps(record.event, ensure_ascii=False)

        return json.dumps(
            {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
            }
        )


json_event_logger = logging.getLogger("event_logger")
json_event_logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
json_event_logger.addHandler(handler)
