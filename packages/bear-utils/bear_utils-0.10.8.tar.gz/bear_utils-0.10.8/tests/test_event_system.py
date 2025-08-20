import pytest

from bear_utils import set_callback, remove_callback, event_call, event_dispatch, clear_callbacks, clear_all


def mock_callback(*args, **kwargs):
    """A simple mock callback function."""
    return "callback called"


class MockClass:
    """A mock class with a method to be used as a callback."""

    def mock_method(self, *args, **kwargs):
        return "class method called"


@pytest.fixture(autouse=True)
def reset_event_system():
    """Fixture to reset the event system before each test."""
    clear_all()


@pytest.mark.asyncio
async def test_basic_function_callback():
    """Test registering and dispatching to a basic function callback."""
    set_callback("test_event", mock_callback)

    await event_dispatch("test_event")

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "callback called"
    assert len(failures) == 0


@pytest.mark.asyncio
async def test_method_callback():
    """Test registering and dispatching to a class method callback."""
    obj = MockClass()
    set_callback("test_event", obj.mock_method)

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "class method called"
    assert len(failures) == 0


@pytest.mark.asyncio
async def test_multiple_callbacks():
    """Test multiple callbacks for the same event."""
    obj = MockClass()
    set_callback("test_event", mock_callback)
    set_callback("test_event", obj.mock_method)

    successes, failures = await event_call("test_event")
    assert len(successes) == 2
    assert "callback called" in successes
    assert "class method called" in successes
    assert len(failures) == 0


@pytest.mark.asyncio
async def test_event_dispatch_vs_event_call():
    """Test that event_dispatch returns None while event_call returns results."""
    set_callback("test_event", mock_callback)

    result = await event_dispatch("test_event")
    assert result is None

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "callback called"


@pytest.mark.asyncio
async def test_nonexistent_event():
    """Test dispatching to an event with no callbacks."""
    result = await event_dispatch("nonexistent_event")
    assert result is None

    successes, failures = await event_call("nonexistent_event")
    assert len(successes) == 0
    assert len(failures) == 0


@pytest.mark.asyncio
async def test_callback_with_args_kwargs():
    """Test callbacks receive args and kwargs correctly."""

    def arg_callback(x, y, z=None):
        return f"args: {x}, {y}, kwargs: {z}"

    set_callback("test_event", arg_callback)

    successes, failures = await event_call("test_event", "hello", "world", z="test")
    assert len(successes) == 1
    assert successes[0] == "args: hello, world, kwargs: test"


@pytest.mark.asyncio
async def test_async_callbacks():
    """Test mixing async and sync callbacks."""

    async def async_callback():
        return "async called"

    def sync_callback():
        return "sync called"

    set_callback("test_event", async_callback)
    set_callback("test_event", sync_callback)

    successes, failures = await event_call("test_event")
    assert len(successes) == 2
    assert "async called" in successes
    assert "sync called" in successes
    assert len(failures) == 0


@pytest.mark.asyncio
async def test_callback_exceptions():
    """Test that callback exceptions are captured properly."""

    def working_callback():
        return "success"

    def failing_callback():
        raise ValueError("test error")

    async def async_failing_callback():
        raise RuntimeError("async error")

    set_callback("test_event", working_callback)
    set_callback("test_event", failing_callback)
    set_callback("test_event", async_failing_callback)

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "success"
    assert len(failures) == 2
    assert any(isinstance(f, ValueError) and str(f) == "test error" for f in failures)
    assert any(isinstance(f, RuntimeError) and str(f) == "async error" for f in failures)


@pytest.mark.asyncio
async def test_remove_callback():
    """Test removing specific callbacks."""
    obj = MockClass()

    set_callback("test_event", mock_callback)
    set_callback("test_event", obj.mock_method)

    successes, failures = await event_call("test_event")
    assert len(successes) == 2

    removed = remove_callback("test_event", mock_callback)
    assert removed is True

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "class method called"

    nonexistent_removed = remove_callback("test_event", mock_callback)
    assert nonexistent_removed is False


@pytest.mark.asyncio
async def test_clear_callbacks():
    """Test clearing all callbacks for a specific event."""
    obj = MockClass()

    set_callback("test_event", mock_callback)
    set_callback("test_event", obj.mock_method)
    set_callback("other_event", mock_callback)

    clear_callbacks("test_event")

    successes, failures = await event_call("test_event")
    assert len(successes) == 0

    successes, failures = await event_call("other_event")
    assert len(successes) == 1


@pytest.mark.asyncio
async def test_weak_reference_cleanup():
    """Test that callbacks are cleaned up when objects are deleted."""

    class TempClass:
        def temp_method(self):
            return "temp called"

    obj = TempClass()
    set_callback("test_event", obj.temp_method)
    set_callback("test_event", mock_callback)

    successes, failures = await event_call("test_event")
    assert len(successes) == 2

    del obj
    import gc

    gc.collect()

    successes, failures = await event_call("test_event")
    assert len(successes) == 1
    assert successes[0] == "callback called"
