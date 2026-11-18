import logging
import re
import structlog

_PII_PATTERNS = [
    (re.compile(r"\+?\d[\d\s\-()]{7,}\d"), "[PHONE_REDACTED]"),
    (re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"), "[EMAIL_REDACTED]"),
]


def _redact_pii(_, __, event_dict):
    msg = str(event_dict.get("event", ""))
    for pattern, repl in _PII_PATTERNS:
        msg = pattern.sub(repl, msg)
    event_dict["event"] = msg
    return event_dict


def configure_logging(debug: bool = False) -> None:
    logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _redact_pii,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if debug else logging.INFO
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "bellia"):
    return structlog.get_logger(name)