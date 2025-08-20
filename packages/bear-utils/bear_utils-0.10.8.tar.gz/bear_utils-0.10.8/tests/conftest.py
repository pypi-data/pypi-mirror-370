import pytest


class DummyLogger:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def info(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("info", str(msg)))

    def warning(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("warning", str(msg)))

    def success(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("success", str(msg)))

    def failure(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("failure", str(msg)))

    def error(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("error", str(msg)))

    def verbose(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("verbose", str(msg)))

    def debug(self, msg: object, *args, **kwargs) -> None:
        self.messages.append(("debug", str(msg)))


@pytest.fixture
def logger() -> DummyLogger:
    return DummyLogger()
