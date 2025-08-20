"""FastAPI-based local logging server and HTTP logger."""

import asyncio
from collections import deque
from pathlib import Path
import threading
from typing import TYPE_CHECKING, Any, Self, TextIO

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from pydantic import BaseModel, Field, field_serializer
from singleton_base import SingletonBase
import uvicorn

from bear_utils.constants import DEVNULL, ExitCode, HTTPStatusCode
from bear_utils.logger_manager._log_level import LogLevel
from bear_utils.time import EpochTimestamp

if TYPE_CHECKING:
    from httpx import Response


class LogRequest(BaseModel):
    """Request model for logging messages."""

    level: LogLevel | int | str = Field(default=LogLevel.DEBUG, description="Log level of the message")
    message: str = Field(default="", description="Log message content")
    args: tuple = Field(default=(), description="Arguments for the log message")
    kwargs: dict[str, str] = Field(default_factory=dict, description="Keyword arguments for the log message")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    @field_serializer("level")
    def serialize_level(self, value: LogLevel | int | str) -> int:
        """Serialize the log level to an integer."""
        return LogLevel.get(value, default=LogLevel.DEBUG).value


class LoggingServer[T: TextIO](SingletonBase):
    """A local server that writes logs to a file."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        log_file: str | Path = "server.log",
        level: LogLevel | int | str = LogLevel.DEBUG,
        file: T = DEVNULL,  # Default to DEVNULL to discard console output
        maxlen: int = 100,
    ) -> None:
        """Initialize the logging server."""
        self.host: str = host
        self.port: int = port
        self.log_file: Path = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        self.app = FastAPI()
        self.server_thread = None
        self._running = False
        self.logs: deque[LogRequest] = deque(maxlen=maxlen)
        self.file: T = file
        self._setup_routes()

    @property
    def running(self) -> bool:
        """Check if the server is running."""
        return self._running or (self.server_thread is not None and self.server_thread.is_alive())

    def __len__(self) -> int:
        """Get the number of logged messages."""
        return len(self.logs)

    def get_logs(self) -> list[LogRequest]:
        """Get the list of logged messages."""
        return list(self.logs)

    def print(self, msg: object, end: str = "\n") -> None:
        """Print the message to the specified file with an optional end character."""
        print(msg, end=end, file=self.file)

    def response(
        self,
        status: str,
        message: str = "",
        status_code: HTTPStatusCode = HTTPStatusCode.SERVER_OK,
    ) -> JSONResponse:
        """Create a JSON response with the given content and status code."""
        return JSONResponse(content={"status": status, "message": message}, status_code=status_code.value)

    def _setup_routes(self) -> None:
        """Set up the FastAPI routes for logging and health check."""

        @self.app.post("/log")
        async def log_message(request: LogRequest | Any) -> JSONResponse:
            """Endpoint to log a message."""
            request = LogRequest(
                level=request["level"] if isinstance(request, dict) else request.level,
                message=request["message"] if isinstance(request, dict) else request.message,
                args=request["args"] if isinstance(request, dict) else request.args,
                kwargs=request["kwargs"] if isinstance(request, dict) else request.kwargs,
            )
            level: LogLevel = LogLevel.get(request.level, default=LogLevel.DEBUG)
            if level.value < self.level.value:
                return self.response(status="ignored", message="Log level is lower than server's minimum level")
            message = request.message
            args = request.args
            kwargs: dict[str, str] | Any = request.kwargs
            success: ExitCode = self.write_log(level, message, *args, **kwargs)
            self.logs.append(request)
            if success != ExitCode.SUCCESS:
                return self.response(
                    status="error", message="Failed to write log", status_code=HTTPStatusCode.SERVER_ERROR
                )
            return self.response(status="success", status_code=HTTPStatusCode.SERVER_OK)

        @self.app.get("/health")
        async def health_check() -> JSONResponse:
            return JSONResponse(
                content={"status": "healthy"},
                status_code=HTTPStatusCode.SERVER_OK,
            )

    def write_log(
        self,
        level: LogLevel,
        message: str,
        end: str = "\n",
        *args,
        **kwargs,
    ) -> ExitCode:
        """Write a log entry to the file - same logic as original logger."""
        timestamp: str = EpochTimestamp.now().to_string()
        log_entry: str = f"[{timestamp}] {level}: {message}"
        buffer = []
        try:
            buffer.append(log_entry)
            if args:
                buffer.append(f"{end}".join(str(arg) for arg in args))
            if kwargs:
                for key, value in kwargs.items():
                    buffer.append(f"{key}={value}{end}")
            if kwargs.pop("console", False):
                self.print(f"{end}".join(buffer))
            with open(self.log_file, "a", encoding="utf-8") as f:
                for line in buffer:
                    f.write(f"{line}{end}")
            return ExitCode.SUCCESS
        except Exception:
            self.print(f"[{timestamp}] {level}: {message}")
            return ExitCode.FAILURE

    async def start(self) -> None:
        """Start the logging server in a separate thread."""
        if self._running:
            return

        def _run_server() -> None:
            """Run the FastAPI server in a new event loop."""
            uvicorn.run(self.app, host=self.host, port=self.port, log_level="error")

        self.server_thread = threading.Thread(target=_run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self._running = True
        self.write_log(LogLevel.DEBUG, f"Logging server started on {self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the logging server."""
        if self._running:
            self._running = False
            if self.server_thread is not None:
                self.server_thread.join(timeout=1)
                self.server_thread = None
            self.write_log(LogLevel.DEBUG, "Logging server stopped")

    async def __aenter__(self) -> Self:
        """Start the logging server."""
        if not self.running:
            await self.start()
        else:
            self.write_log(LogLevel.DEBUG, "Logging server is already running")
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Stop the logging server."""
        await self.stop()


class LoggingClient[T: TextIO]:
    """Logger that calls HTTP endpoints but behaves like SimpleLogger."""

    def __init__(
        self,
        server_url: str | None = None,
        host: str = "http://localhost",
        port: int = 8080,
        level: LogLevel | int | str = LogLevel.DEBUG,
        file: T = DEVNULL,  # Default to DEVNULL to discard console output
    ) -> None:
        """Initialize the ServerLogger."""
        self.host: str = host
        self.port: int = port
        self.server_url: str = server_url or f"{self.host}:{self.port}"
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        self.client: AsyncClient = AsyncClient(timeout=5.0)
        self.file: T = file

    async def post(self, url: str, json: dict) -> "Response":
        """Send a POST request to the server."""
        return await self.client.post(url=url, json=json)

    async def _log(self, request: LogRequest) -> None:
        """Same interface as SimpleLogger._log but calls HTTP endpoint."""
        try:
            response: Response = await self.post(url=f"{self.server_url}/log", json=request.model_dump())
            if response.status_code != HTTPStatusCode.SERVER_OK:
                await self._fallback_log(str(request.level), request.message, *request.args, **request.kwargs)
        except Exception:
            await self._fallback_log(str(request.level), request.message, *request.args, **request.kwargs)

    async def log(self, level: LogLevel, msg: object, *args: Any, **kwargs: Any) -> None:
        """Log a message at the specified level."""
        if level.value >= self.level.value:
            request = LogRequest(level=level.value, message=str(msg), args=args, kwargs=kwargs)
            await self._log(request)

    async def _fallback_log(self, lvl: str, msg: object, *args: Any, **kwargs: Any) -> None:
        """Fallback - same as original SimpleLogger._log."""
        timestamp: str = EpochTimestamp.now().to_string()
        print(f"Fallback Logging: [{timestamp}] {lvl}: {msg}", file=self.file)
        if args:
            print(" ".join(str(arg) for arg in args), file=self.file)
        if kwargs:
            for key, value in kwargs.items():
                print(f"{key}={value}", file=self.file)

    async def verbose(self, msg: object, *args, **kwargs) -> None:
        """Log a verbose message."""
        await self.log(LogLevel.VERBOSE, msg, *args, **kwargs)

    async def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        await self.log(LogLevel.DEBUG, msg, *args, **kwargs)

    async def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        await self.log(LogLevel.INFO, msg, *args, **kwargs)

    async def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        await self.log(LogLevel.WARNING, msg, *args, **kwargs)

    async def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        await self.log(LogLevel.ERROR, msg, *args, **kwargs)

    async def failure(self, msg: object, *args, **kwargs) -> None:
        """Log a failure message."""
        await self.log(LogLevel.FAILURE, msg, *args, **kwargs)

    async def success(self, msg: object, *args, **kwargs) -> None:
        """Log a success message."""
        await self.log(LogLevel.SUCCESS, msg, *args, **kwargs)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        """Enter the asynchronous context manager."""
        return self

    async def __aexit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the asynchronous context manager."""
        await self.close()


async def run_server(
    host: str = "localhost",
    port: int = 8080,
    log_file: str = "server.log",
    level: LogLevel | int | str = LogLevel.DEBUG,
    file: TextIO = DEVNULL,
) -> ExitCode | int:
    """Run the local logging server."""
    server: LoggingServer[TextIO] = LoggingServer(
        host=host,
        port=port,
        log_file=log_file,
        level=level,
        file=file,
    )
    try:
        while True:
            await server.start()
    except KeyboardInterrupt:
        print("Stopping server...", file=server.file)
    except Exception as e:
        print(f"An error occurred: {e}", file=server.file)
        return ExitCode.FAILURE
    finally:
        await server.stop()
    return ExitCode.SUCCESS


def sync_server(
    host: str = "localhost",
    port: int = 8080,
    log_file: str = "server.log",
    level: LogLevel | int | str = LogLevel.DEBUG,
    file: TextIO = DEVNULL,
) -> ExitCode | int:
    """Run the local logging server synchronously."""
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(run_server(host, port, log_file, level, file))


# if __name__ == "__main__":
#     exit_code = sync_server()
#     sys.exit(exit_code)
