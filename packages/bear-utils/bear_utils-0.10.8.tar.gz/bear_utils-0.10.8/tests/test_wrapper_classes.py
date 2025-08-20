import pytest
from unittest.mock import patch
from io import StringIO

from bear_utils.extras import BaseWrapper, StringIOWrapper
from bear_utils.extras.utility_classes._wrapper import InputObjectError, OutputObjectError


class MockValidateType:
    """Mock validate_type function for testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, obj, expected_type, error_class):
        self.calls.append((obj, expected_type, error_class))
        if not isinstance(obj, expected_type):
            raise error_class(expected_type, type(obj))


@pytest.fixture
def mock_type_param():
    """Mock type_param to return predictable types for testing."""

    def _mock_type_param(cls, index=0):
        type_map = {
            "StringIOWrapper": [StringIO, str],
            "TestWrapper": [str, int],
            "InvalidWrapper": [str, int],
        }
        types = type_map.get(cls.__name__, [str, str])
        return types[index] if index < len(types) else str

    with patch("bear_utils.extras._tools.type_param", side_effect=_mock_type_param):
        yield


@pytest.fixture
def mock_validate_type():
    """Mock validate_type function."""
    mock_validator = MockValidateType()
    with patch("bear_utils.extras.utility_classes._wrapper.validate_type", side_effect=mock_validator):
        yield mock_validator


class TestInputOutputErrors:
    """Test custom error classes."""

    def test_input_object_error(self):
        """Test InputObjectError message formatting."""
        error = InputObjectError(str, int)
        assert str(error) == "Expected input object of type str, but got int."

    def test_output_object_error(self):
        """Test OutputObjectError message formatting."""
        error = OutputObjectError(list, dict)
        assert str(error) == "Expected output object of type list, but got dict."


class TestBaseWrapper:
    """Test BaseWrapper functionality."""

    def test_init_with_both_objects(self, mock_type_param, mock_validate_type):
        """Test initialization with both incoming and outgoing objects."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("hello", 42)

        assert wrapper.root_obj == "hello"
        assert wrapper.cache_obj == 42
        assert len(mock_validate_type.calls) == 2

    def test_init_with_none_creates_defaults(self, mock_type_param, mock_validate_type):
        """Test initialization with None creates default objects."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper(None, None)

        assert wrapper.root_obj == ""  # str()
        assert wrapper.cache_obj == 0  # int()
        assert len(mock_validate_type.calls) == 2

    def test_init_partial_none(self, mock_type_param, mock_validate_type):
        """Test initialization with one None argument."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("test", None)

        assert wrapper.root_obj == "test"
        assert wrapper.cache_obj == 0  # int()

    def test_type_param_called_correctly(self, mock_type_param, mock_validate_type):
        """Test that type_param is called with correct parameters."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        with patch("bear_utils.extras.utility_classes._wrapper.type_param") as mock_tp:
            mock_tp.side_effect = lambda cls, idx: [str, int][idx]

            TestWrapper("test", 42)

            # Should be called twice: once for index 0, once for index 1
            assert mock_tp.call_count == 2
            mock_tp.assert_any_call(TestWrapper, 0)
            mock_tp.assert_any_call(TestWrapper, 1)

    def test_validate_type_called_correctly(self, mock_type_param, mock_validate_type):
        """Test that validate_type is called with correct parameters."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("test", 42)

        # Should validate both incoming and outgoing
        assert len(mock_validate_type.calls) == 2

        incoming_call = mock_validate_type.calls[0]
        assert incoming_call[0] == "test"
        assert incoming_call[1] == str
        assert incoming_call[2] == InputObjectError

        outgoing_call = mock_validate_type.calls[1]
        assert outgoing_call[0] == 42
        assert outgoing_call[1] == int
        assert outgoing_call[2] == OutputObjectError


class TestBaseWrapperProperties:
    """Test BaseWrapper properties."""

    def test_root_obj_property(self, mock_type_param, mock_validate_type):
        """Test root_obj property returns correct object."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("test", 42)
        assert wrapper.root_obj == "test"

    def test_cache_obj_property_get(self, mock_type_param, mock_validate_type):
        """Test cache_obj property getter."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("test", 42)
        assert wrapper.cache_obj == 42

    def test_cache_obj_property_set_valid(self, mock_type_param, mock_validate_type):
        """Test cache_obj property setter with valid type."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        wrapper = TestWrapper("test", 42)
        wrapper.cache_obj = 100

        assert wrapper.cache_obj == 100
        # Should have 3 validate_type calls: 2 from init + 1 from setter
        assert len(mock_validate_type.calls) == 3

    def test_cache_obj_property_set_invalid(self, mock_type_param):
        """Test cache_obj property setter with invalid type raises error."""

        class TestWrapper(BaseWrapper[str, int]):
            pass

        # Mock validate_type to raise error for wrong type
        def mock_validate(obj, expected_type, error_class):
            if not isinstance(obj, expected_type):
                raise error_class(expected_type, type(obj))

        with patch("bear_utils.extras._tools.validate_type", side_effect=mock_validate):
            wrapper = TestWrapper("test", 42)

            with pytest.raises(OutputObjectError):
                wrapper.cache_obj = "wrong_type"  # type: ignore[arg-type str instead of int]


class TestStringIOWrapper:
    """Test StringIOWrapper functionality."""

    def test_init_with_defaults(self, mock_type_param, mock_validate_type):
        """Test StringIOWrapper initialization with default values."""
        wrapper = StringIOWrapper()

        assert isinstance(wrapper.root_obj, StringIO)
        assert isinstance(wrapper.cache_obj, str)
        assert wrapper.cache_obj == ""

    def test_init_with_custom_objects(self, mock_type_param, mock_validate_type):
        """Test StringIOWrapper initialization with custom objects."""
        custom_io = StringIO("initial")
        wrapper = StringIOWrapper(custom_io, "cached")

        assert wrapper.root_obj is custom_io
        assert wrapper.cache_obj == "cached"

    def test_write_single_value(self, mock_type_param, mock_validate_type):
        """Test writing a single value."""
        wrapper = StringIOWrapper()
        wrapper.write("hello")

        assert wrapper.root_obj.getvalue() == "hello"

    def test_write_multiple_values(self, mock_type_param, mock_validate_type):
        """Test writing multiple values."""
        wrapper = StringIOWrapper()
        wrapper.write("hello", " ", "world")

        assert wrapper.root_obj.getvalue() == "hello world"

    def test_cache_method(self, mock_type_param, mock_validate_type):
        """Test cache method saves current content."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")

        result = wrapper.cache()

        assert wrapper.cache_obj == "test content"
        assert result is wrapper  # Returns self for chaining

    def test_reset_without_clear(self, mock_type_param, mock_validate_type):
        """Test reset method without clearing cache."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")

        result = wrapper.reset(clear=False)

        # Cache should contain the content
        assert wrapper.cache_obj == "test content"
        # StringIO should be empty
        assert wrapper.root_obj.getvalue() == ""
        assert result is wrapper  # Returns self for chaining

    def test_reset_with_clear(self, mock_type_param, mock_validate_type):
        """Test reset method with clearing cache."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")

        result = wrapper.reset(clear=True)

        # Cache should be empty
        assert wrapper.cache_obj == ""
        # StringIO should be empty
        assert wrapper.root_obj.getvalue() == ""
        assert result is wrapper

    def test_flush_method(self, mock_type_param, mock_validate_type):
        """Test flush method (alias for reset without clear)."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")

        wrapper.flush()

        assert wrapper.cache_obj == "test content"
        assert wrapper.root_obj.getvalue() == ""

    def test_getvalue_from_root_when_not_empty(self, mock_type_param, mock_validate_type):
        """Test getvalue returns from root when root has content."""
        wrapper = StringIOWrapper()
        wrapper.cache_obj = "cached content"
        wrapper.write("new content")

        # Should return from root_obj since it has content
        assert wrapper.getvalue() == "new content"

    def test_getvalue_from_cache_when_root_empty(self, mock_type_param, mock_validate_type):
        """Test getvalue returns from cache when root is empty."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")
        wrapper.reset(clear=False)  # Clear root_obj

        # Should return from cache since root is empty
        assert wrapper.getvalue(cache=True) == "test content"

    def test_private_reset_method(self, mock_type_param, mock_validate_type):
        """Test _reset private method behavior."""
        wrapper = StringIOWrapper()
        wrapper.write("test content")

        # Test _reset without clear
        wrapper._reset(clear=False)
        assert wrapper.cache_obj == "test content"
        assert wrapper.root_obj.getvalue() == ""

        # Write new content and test _reset with clear
        wrapper.write("new content")
        wrapper._reset(clear=True)
        assert wrapper.cache_obj == ""
        assert wrapper.root_obj.getvalue() == ""


class TestStringIOWrapperMethodChaining:
    """Test method chaining in StringIOWrapper."""

    def test_fluent_interface(self, mock_type_param, mock_validate_type):
        """Test that methods return self for chaining."""
        wrapper = StringIOWrapper()

        result = wrapper.cache().reset(clear=False).reset(clear=True)

        assert result is wrapper


class TestStringIOWrapperEdgeCases:
    """Test edge cases for StringIOWrapper."""

    def test_multiple_writes_and_operations(self, mock_type_param, mock_validate_type):
        """Test complex sequence of operations."""
        wrapper = StringIOWrapper()

        # Write, cache, write more, flush
        wrapper.write("first")
        wrapper.cache()
        wrapper.write(" second")
        wrapper.flush()

        assert wrapper.getvalue(cache=True) == "first second"
        assert wrapper.root_obj.getvalue() == ""

    def test_reset_behavior_with_existing_cache(self, mock_type_param, mock_validate_type):
        """Test reset behavior when cache already has content."""
        wrapper = StringIOWrapper()
        wrapper.cache_obj = "existing cache"
        wrapper.write("new content")

        # Reset without clear should overwrite cache
        wrapper.reset(clear=False)
        assert wrapper.cache_obj == "new content"

        # Reset with clear should clear cache
        wrapper.write("more content")
        wrapper.reset(clear=True)
        assert wrapper.cache_obj == ""

    def test_empty_string_io_operations(self, mock_type_param, mock_validate_type):
        """Test operations on empty StringIO."""
        wrapper = StringIOWrapper()

        # Operations on empty StringIO
        assert wrapper.getvalue() == ""
        wrapper.cache()
        assert wrapper.cache_obj == ""
        wrapper.flush()
        assert wrapper.cache_obj == ""
