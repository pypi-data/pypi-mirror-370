# ruff: noqa: G201
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TextIO
from unittest.mock import patch

import anyio
import httpx
import pytest

from bear_utils import BufferLogger, ConsoleLogger, FileLogger
from bear_utils.constants import DEVNULL, HTTPStatusCode
from bear_utils.extras import ascii_header as fmt_header
from bear_utils.logger_manager import (
    AsyncLoggerProtocol,
    LogConsole as Console,
    LoggerProtocol,
    LoggingClient,
    LoggingServer,
    LogLevel,
    SimpleLogger,
)
from bear_utils.logger_manager._log_level import DEBUG, INFO, VERBOSE, WARNING

console = Console()


class TestLoggerFactory:
    """Factory for creating test logger instances."""

    @staticmethod
    def create_console_logger(**kwargs) -> ConsoleLogger:
        """Create a ConsoleLogger instance for testing."""
        if ConsoleLogger.has_instance():
            ConsoleLogger.reset_instance()

            import logging  # noqa: PLC0415

            logging.getLogger().handlers.clear()

        defaults = {
            "name": "TestConsole",
            "level": VERBOSE,
            "file": False,
            "console": True,
            "queue_handler": False,
            "buffering": False,
            "style_disabled": False,
            "logger_mode": True,
        }
        defaults.update(kwargs)
        return ConsoleLogger.get_instance(init=True, **defaults)

    @staticmethod
    def create_file_logger(**kwargs) -> FileLogger:
        """Create a FileLogger instance for testing."""
        if FileLogger.has_instance():
            FileLogger.reset_instance()

            import logging  # noqa: PLC0415

            logging.getLogger().handlers.clear()

        defaults = {
            "name": "TestFileLogger",
            "level": DEBUG,
            "file_path": Path("tests") / "test_log.log",
            "max_bytes": 5 * 1024 * 1024,  # 5 MB
            "backup_count": 5,
        }
        defaults.update(kwargs)
        return FileLogger.get_instance(init=True, **defaults)

    @staticmethod
    def create_buffer_logger(**kwargs) -> BufferLogger:
        """Create a BufferLogger instance for testing."""
        if BufferLogger.has_instance():
            BufferLogger.reset_instance()

            import logging  # noqa: PLC0415

            logging.getLogger().handlers.clear()

        defaults = {"name": "TestBufferLogger", "level": DEBUG, "width": 80}
        defaults.update(kwargs)
        return BufferLogger.get_instance(init=True, **defaults)


class TestBasicLogging:
    """Test basic logging functionality."""

    def test_log_level_filtering_works(self):
        """Test that log level filtering actually works"""
        logger = TestLoggerFactory.create_console_logger(level=INFO)

        assert isinstance(logger, LoggerProtocol), "ConsoleLogger should implement LoggerProtocol"
        captured_messages = []
        original_print = logger._print

        fmt_header("Test Log Level Filtering")

        def capture_print(msg, end, *args, **kwargs) -> None:
            captured_messages.append(str(msg))
            return original_print(msg, end, *args, **kwargs)

        with patch.object(logger, "_print", capture_print):
            logger.info("Should appear")
            logger.debug("Should NOT appear")
            logger.error("Should also appear")

        debug_msg = f"Expected 2 messages, got {len(captured_messages)}: Logger Debugging: {logger}"
        assert len(captured_messages) == 2, debug_msg
        assert any("Should appear" in msg for msg in captured_messages)
        assert any("Should also appear" in msg for msg in captured_messages)
        assert not any("Should NOT appear" in msg for msg in captured_messages)

    @pytest.mark.visual
    def test_exception_logging(self):
        """Test that exceptions are logged correctly."""
        logger = TestLoggerFactory.create_console_logger(level=DEBUG)

        assert isinstance(logger, LoggerProtocol), "ConsoleLogger should implement LoggerProtocol"
        captured_messages = []
        original_print = logger._print

        fmt_header("Test Exception Logging")

        def capture_print(msg, end, *args, **kwargs) -> None:
            captured_messages.append(str(msg))
            return original_print(msg, end, *args, **kwargs)

        with patch.object(logger, "_print", capture_print):
            try:
                v: float = 200 / 0  # noqa: F841 # Intentionally cause a ZeroDivisionError
            except Exception:
                logger.exception("Test")

    def test_sub_logger_inherits_level(self):
        """Test that sub logger inherits the level from the parent logger."""
        parent_logger = TestLoggerFactory.create_console_logger(level=INFO)
        sub_logger = parent_logger.get_sub_logger("SubLogger")

        captured_messages = []

        original_print = parent_logger._print

        fmt_header("Test Sub Logger Inherits Level")

        def capture_print(msg, end, *args, **kwargs) -> None:
            captured_messages.append(str(msg))
            return original_print(msg, end, *args, **kwargs)

        with patch.object(parent_logger, "_print", capture_print):
            sub_logger.info("This should appear")
            sub_logger.debug("This should NOT appear")
            sub_logger.verbose("This should NOT appear either")

        assert len(captured_messages) == 1
        assert "This should appear" in captured_messages[0]
        assert "This should NOT appear" not in captured_messages[0]

    def test_sub_logger_custom_level(self):
        """Test that sub logger can have a custom level."""
        fmt_header("Test Sub Logger Custom Level")

        parent_logger = TestLoggerFactory.create_console_logger(level=DEBUG)
        sub_logger = parent_logger.get_sub_logger("SubLogger", level=WARNING)

        captured_messages = []

        original_print = parent_logger._print

        def capture_print(msg, end, *args, **kwargs) -> None:
            captured_messages.append(str(msg))
            return original_print(msg, end, *args, **kwargs)

        with patch.object(parent_logger, "_print", capture_print):
            sub_logger.info("This should NOT appear")
            sub_logger.warning("This should appear")
            sub_logger.error("This should also appear")
            sub_logger.failure("This should also appear")

        assert len(captured_messages) == 3
        assert "This should appear" in captured_messages[0]
        assert "This should also appear" in captured_messages[1]
        assert "This should NOT appear" not in captured_messages


class TestFileLogging:
    """Test file logging functionality."""

    def test_file_logging(self):
        """Test that file logging works correctly."""
        log_file: Path = Path("tests") / "test_log.log"
        if log_file.exists():
            log_file.unlink()

        logger: FileLogger = FileLogger.get_instance(init=True, name="TestFileLogger", file_path=log_file, level=DEBUG)
        fmt_header("Test File Logging")

        assert isinstance(logger, LoggerProtocol), "FileLogger should implement LoggerProtocol"

        logger.info("This is an info message")
        logger.error("This is an error message")
        logger.debug("This is a debug message")
        logger.warning("This is a warning message")
        logger.success("This is a success message")
        logger.failure("This is a failure message")
        logger.verbose("This is a verbose message")

        assert log_file.exists(), "Log file was not created"
        with open(log_file) as f:
            log_content = f.read()

        assert "This is an info message" in log_content
        assert "This is an error message" in log_content
        assert "This is a debug message" in log_content
        assert "This is a warning message" in log_content
        assert "This is a success message" in log_content
        assert "This is a failure message" in log_content
        assert "This is a verbose message" not in log_content

        if log_file.exists():
            log_file.unlink()


class TestVisualVerification:
    """Tests that require visual inspection of output."""

    @pytest.mark.visual
    def test_all_log_levels_visual(self, capsys):
        """Visual test for all log levels - run with pytest -s"""
        logger = TestLoggerFactory.create_console_logger()

        with capsys.disabled():
            fmt_header("Visual Test: All Log Levels")

            logger.info("This is an info message")
            logger.error("This is an error message")
            logger.debug("This is a debug message")
            logger.warning("This is a warning message")
            logger.success("This is a success message")
            logger.failure("This is a failure message")
            logger.verbose("This is a verbose message")

    @pytest.mark.visual
    def test_sub_logger_visual(self, capsys):
        """Visual test for sub logger - run with pytest -s"""
        parent_logger = TestLoggerFactory.create_console_logger()
        sub_logger = parent_logger.get_sub_logger("SubLogger")

        with capsys.disabled():
            fmt_header("Visual Test: Sub Logger")

            sub_logger.info("This is an info message from the sub logger")
            sub_logger.warning("This is a warning message from the sub logger")
            sub_logger.error("This is an error message from the sub logger")
            sub_logger.debug("This is a debug message from the sub logger")
            sub_logger.success("This is a success message from the sub logger")
            sub_logger.failure("This is a failure message from the sub logger")
            sub_logger.verbose("This is a verbose message from the sub logger")

    @pytest.mark.visual
    def test_traceback_visual(self, capsys):
        """Visual test for traceback - run with pytest -s"""
        logger: ConsoleLogger = TestLoggerFactory.create_console_logger()

        with capsys.disabled():
            fmt_header("Visual Test: Traceback Verification")
            try:
                v: float = 200 / 0  # noqa: F841 # Intentionally cause a ZeroDivisionError
            except Exception:
                logger.error("Test", exc_info=True)

    @pytest.mark.visual
    def test_sub_logger_traceback_visual(self, capsys):
        """Visual test for sub logger traceback - run with pytest -s"""
        parent_logger = TestLoggerFactory.create_console_logger()
        sub_logger = parent_logger.get_sub_logger("SubLogger")

        with capsys.disabled():
            fmt_header("Visual Test: Sub Logger Traceback Verification")

            try:
                v: float = 200 / 0  # noqa: F841 # Intentionally cause a ZeroDivisionError
            except Exception:
                sub_logger.error("SubLogger Test", exc_info=True)

    class TestBufferLogger:
        """Test the BufferLogger functionality."""

        def test_buffer_logger(self):
            """Test that BufferLogger works correctly."""
            from contextlib import redirect_stdout  # noqa: PLC0415
            from io import StringIO  # noqa: PLC0415

            logger: BufferLogger = TestLoggerFactory.create_buffer_logger()

            fmt_header("Test Buffer Logger")

            assert isinstance(logger, LoggerProtocol), "BufferLogger should implement LoggerProtocol"
            stdout_testing = StringIO()
            with redirect_stdout(stdout_testing):
                logger.info("This is an info message in the buffer")
                logger.error("This is an error message in the buffer")
                logger.debug("This is a debug message in the buffer")
                logger.warning("This is a warning message in the buffer")
                logger.success("This is a success message in the buffer")
                logger.failure("This is a failure message in the buffer")
                logger.verbose("This is a verbose message in the buffer")
            output = stdout_testing.getvalue()
            assert output == "", "BufferLogger should not print to stdout directly"

            output = logger.trigger_buffer_flush()
            # if the testing terminal is too small, the output will have \n ended in the middle and break
            assert "This is an info message in the buffer" in output
            assert "This is an error message in the buffer" in output
            assert "This is a debug message in the buffer" in output
            assert "This is a warning message in the buffer" in output
            assert "This is a success message in the buffer" in output
            assert "This is a failure message in the buffer" in output
            assert "This is a verbose message in the buffer" not in output  # Debug level means verbose is not "printed"
            logger.print(output, title="Standard Logger Test")

        @pytest.mark.visual
        def test_traceback_buffer_logger(self, capsys):
            """Visual test for BufferLogger traceback - run with pytest -s"""
            logger: BufferLogger = TestLoggerFactory.create_buffer_logger()

            with capsys.disabled():
                fmt_header("Visual Test: Buffer Logger Traceback Verification")

                try:
                    v: float = 200 / 0  # noqa: F841 # Intentionally cause a ZeroDivisionError
                except Exception:
                    logger.error("BufferLogger Test happened on purpose!", exc_info=True)

                output = logger.trigger_buffer_flush()
                logger.print(output, title="Buffer Logger Test")
                assert "BufferLogger Test" in output
                assert "ZeroDivisionError" in output


class TestSimpleLogger:
    """Test the SimpleLogger functionality."""

    @pytest.mark.visual
    def test_simple_logger(self):
        """Test that SimpleLogger works correctly."""
        fmt_header("Test Simple Logger")
        logger: SimpleLogger = SimpleLogger(level="DEBUG")

        assert isinstance(logger, LoggerProtocol), "SimpleLogger should implement LoggerProtocol"

        logger.info("This is an info message in the simple logger")
        logger.error("This is an error message in the simple logger")
        logger.debug("This is a debug message in the simple logger")
        logger.warning("This is a warning message in the simple logger")
        logger.success("This is a success message in the simple logger")
        logger.failure("This is a failure message in the simple logger")
        logger.verbose("This is a verbose message in the simple logger")


class TestServerLogger:
    """Test the ServerLogger functionality."""

    file_path: Path = Path("tests") / "test_server.log"

    def setup_method(self, _) -> None:
        """Runs before EVERY test method in this class."""
        if self.file_path.exists():
            self.file_path.unlink()

    @asynccontextmanager
    async def get_server_logger(
        self,
        host: str = "localhost",
        port: int = 8093,
        level: LogLevel | int | str = VERBOSE,
        file: TextIO = DEVNULL,
        **kwargs,
    ):
        """Get a ServerLogger instance as an async context manager."""
        if LoggingServer.has_instance():
            instance = LoggingServer.get_instance()
            if instance.running:
                await instance.stop()
                await anyio.sleep(5.0)
            LoggingServer.reset_instance()
            instance = None
            assert not LoggingServer.has_instance(), "LoggingServer instance should be reset"

        server = LoggingServer.get_instance(
            init=True,
            host=host,
            port=port,
            level=level,
            file=file,
            **kwargs,
        )
        try:
            yield server
        finally:
            if server.running:
                await server.stop()
            if LoggingServer.has_instance():
                LoggingServer.reset_instance()

    def _later(self) -> None:
        logger = LoggingClient()
        assert isinstance(logger, AsyncLoggerProtocol), "LoggingClient should implement AsyncLoggerProtocol"

    @pytest.mark.asyncio
    async def test_server(self):
        """Test that LoggingServer works correctly."""

        class TestClient:
            """A mock test client for the FastAPI server."""

            def __init__(self):
                self.host: str = "localhost"
                self.port: int = 8093
                self.client: httpx.AsyncClient = httpx.AsyncClient(base_url=f"http://{self.host}:{self.port}")

            async def api_call(self, method: str, path: str, **kwargs) -> httpx.Response:
                """Mock API request."""
                return await self.client.request(method, path, **kwargs)

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_value, traceback):
                """Mock context manager exit."""
                await self.client.aclose()

        async with self.get_server_logger(port=8093, log_file=self.file_path) as server, TestClient() as mock_client:
            await server.start()
            assert server.running, "Server should be running after start"
            await anyio.sleep(1.0)  # Wait for server to start
            response: httpx.Response = await mock_client.api_call("GET", "/health")
            assert response.status_code == HTTPStatusCode.SERVER_OK, "Health check should return 200 OK"
            response2: httpx.Response = await mock_client.api_call("POST", "/log")
            assert response2.status_code == HTTPStatusCode.UNPROCESSABLE_CONTENT, (
                "POST /log without data should return 422"
            )
            response3: httpx.Response = await mock_client.api_call("GET", "/log")
            assert response3.status_code == HTTPStatusCode.METHOD_NOT_ALLOWED, (
                "GET /log should return 405 Method Not Allowed"
            )
            response4: httpx.Response = await mock_client.api_call(
                "POST", "/log", json={"level": "info", "message": "Test log"}
            )
            assert response4.status_code == HTTPStatusCode.SERVER_OK, "POST /log should return 200 OK"
            assert response4.json() == {"status": "success", "message": ""}, "Response should match expected format"
            assert len(server.logs) == 1, "Server should have one log entry after POST /log"
            await anyio.sleep(1.0)

    @pytest.mark.asyncio
    async def test_server_logger_verbose(self):
        """Test that ServerLogger works correctly."""
        test_port = 8095
        async with (
            self.get_server_logger(port=test_port, level=VERBOSE, log_file=self.file_path) as server,
            LoggingClient(port=test_port, level=VERBOSE) as logger,
        ):
            assert isinstance(logger, AsyncLoggerProtocol), "ServerLogger should implement AsyncLoggerProtocol"
            await server.start()
            await anyio.sleep(1.0)
            assert server.running, "Server should be running after start"
            assert not server.logs, "Server buffer should be empty before logging"
            await logger.info("This is an info message from the server logger")
            await logger.error("This is an error message from the server logger")
            await logger.debug("This is a debug message from the server logger")
            await logger.warning("This is a warning message from the server logger")
            await logger.success("This is a success message from the server logger")
            await logger.failure("This is a failure message from the server logger")
            await logger.verbose("This is a verbose message from the server logger")
            assert len(server) == 7, "Server buffer should have 7 messages after logging"
            assert self.file_path.exists(), "Log file should be created"
            contents: str = self.file_path.read_text(encoding="utf-8")
            assert "This is an info message from the server logger" in contents
            assert "This is an error message from the server logger" in contents
            assert "This is a debug message from the server logger" in contents
            assert "This is a warning message from the server logger" in contents
            assert "This is a success message from the server logger" in contents
            assert "This is a failure message from the server logger" in contents
            assert "This is a verbose message from the server logger" in contents
            await anyio.sleep(1.0)

    def teardown_method(self, _):
        """Runs after EVERY test method in this class."""
        if self.file_path.exists():
            self.file_path.unlink()


if __name__ == "__main__":
    print("Run visual tests with: pytest tests/test_logger.py -m visual -s")
    print("Run all tests with: pytest tests/test_logger.py")
