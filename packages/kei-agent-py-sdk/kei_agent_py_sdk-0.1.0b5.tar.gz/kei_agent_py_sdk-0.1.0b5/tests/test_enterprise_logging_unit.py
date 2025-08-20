import json
import logging
from io import StringIO

import pytest

from kei_agent.enterprise_logging import StructuredFormatter, RedactingFilter, EnterpriseLogger


def make_record(logger: logging.Logger, level=logging.INFO, msg="test", **extra):
    if extra:
        logger = logging.LoggerAdapter(logger, extra)
    logger.log(level, msg)


def capture_logger_output(logger: logging.Logger, level=logging.INFO, msg="test", **extra):
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    try:
        make_record(logger, level=level, msg=msg, **extra)
        handler.flush()
        return stream.getvalue().strip()
    finally:
        logger.removeHandler(handler)


class TestStructuredFormatter:
    def test_basic_format_json_parseable(self):
        logger = logging.getLogger("test.basic")
        out = capture_logger_output(logger, msg="hello")
        data = json.loads(out)
        assert data["message"] == "hello"
        assert data["level"] == "INFO"
        assert data["logger"] == "test.basic"

    def test_with_exception_info(self):
        logger = logging.getLogger("test.exc")
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        try:
            try:
                raise ValueError("boom")
            except ValueError:
                logger.exception("failed")
            handler.flush()
            data = json.loads(stream.getvalue().strip())
            assert data["message"] == "failed"
            assert "exception" in data
            assert data["exception"]["type"] == "ValueError"
        finally:
            logger.removeHandler(handler)

    def test_extra_fields_included(self):
        logger = logging.getLogger("test.extra")
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter(extra_fields={"svc": "sdk"}))
        logger.addHandler(handler)
        try:
            logger.info("msg", extra={"duration": 12})
            handler.flush()
            data = json.loads(stream.getvalue().strip())
            assert data["extra"]["duration"] == 12
            assert data["svc"] == "sdk"
        finally:
            logger.removeHandler(handler)


class TestRedactingFilter:
    def test_redacts_message_keys(self):
        logger = logging.getLogger("test.redact.msg")
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        redactor = RedactingFilter()
        logger.addFilter(redactor)
        handler.addFilter(redactor)
        logger.addHandler(handler)
        try:
            logger.info("token=SECRET secret=VALUE password=PW")
            handler.flush()
            out = stream.getvalue()
            assert "token" not in out
            assert "secret" not in out
            assert "password" not in out
            assert "***" in out
        finally:
            logger.removeFilter(redactor)
            logger.removeHandler(handler)

    def test_redacts_extra_fields(self):
        logger = logging.getLogger("test.redact.extra")
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        redactor = RedactingFilter()
        logger.addFilter(redactor)
        handler.addFilter(redactor)
        logger.addHandler(handler)
        try:
            logger.info("msg", extra={"api_key": "ABCDE", "client_secret": "XYZ"})
            handler.flush()
            data = json.loads(stream.getvalue().strip())
            assert data["extra"]["api_key"] == "***"
            assert data["extra"]["client_secret"] == "***"
        finally:
            logger.removeFilter(redactor)
            logger.removeHandler(handler)


class TestEnterpriseLogger:
    def test_initialization_and_handlers(self):
        el = EnterpriseLogr(
            name="test.enterprise",
            enable_structured=True,
            enable_console=True,
            enable_file=False,
            extra_fields={"component": "test"},
        )
        logger = el.logger
        assert isinstance(logger, logging.Logger)
        # At least one handler is attached
        assert logger.handlers
        # Ensure redactor is attached either on logger or handlers
        has_redactor = any(isinstance(f, RedactingFilter) for f in logger.filters)
        has_redactor |= any(any(isinstance(f, RedactingFilter) for f in h.filters) for h in logger.handlers)
        assert has_redactor, "RedactingFilter should be attached"
