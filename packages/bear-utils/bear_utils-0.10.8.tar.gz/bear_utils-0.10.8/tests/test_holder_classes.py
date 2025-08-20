import pytest
from unittest.mock import patch, Mock
from io import StringIO
from collections import defaultdict

from bear_utils.extras.utility_classes._holder import ObjectHolder, GenericClassProperties, StringSpace, BufferSpace


@pytest.fixture
def mock_type_param():
    """Mock type_param to return predictable types for testing."""

    def _mock_type_param(cls, index=0):
        print(f"Mocking type_param for {cls} at index {index}")
        type_map = {
            "StringSpace": str,
            "BufferSpace": StringIO,
            "TestHolder": int,
        }
        return type_map.get(cls.__name__, str)

    with patch("bear_utils.extras.utility_classes._holder.type_param", side_effect=_mock_type_param):
        yield


class TestMetaWithProperties:
    """Test the metaclass behavior."""

    def test_type_property_access(self, mock_type_param):
        """Test that _type property returns correct type."""
        assert StringSpace._cls_type_param(0) == str
        assert BufferSpace._cls_type_param(0) == StringIO

    def test_type_property_different_classes(self, mock_type_param):
        """Test that different classes get different types."""

        class TestHolder(ObjectHolder[int]):
            pass

        assert TestHolder._cls_type_param(0) == int
        assert StringSpace._cls_type_param(0) == str


class TestObjectHolder:
    """Test the base ObjectHolder functionality."""

    def test_init_with_default(self, mock_type_param):
        """Test initialization with a default value."""
        holder = StringSpace("hello")
        assert holder.active == "hello"
        assert holder.current == "default"

    def test_init_without_default(self, mock_type_param):
        """Test initialization without default creates empty object."""
        holder = StringSpace()
        assert holder.active == ""  # str() creates empty string
        assert holder.current == "default"

    def test_init_wrong_type_raises_error(self, mock_type_param):
        """Test that wrong type for default raises TypeError."""
        with pytest.raises(TypeError):
            StringSpace(123)  # type: ignore[arg-type int instead of str]

    def test_cls_property(self, mock_type_param):
        """Test that cls property returns the correct class."""
        holder = StringSpace()
        assert holder._class == StringSpace

    def test_container_is_defaultdict(self, mock_type_param):
        """Test that _container is a defaultdict with correct factory."""
        holder = StringSpace()
        assert isinstance(holder._container, defaultdict)
        # Accessing new key should create default object
        new_value = holder._container["new_key"]
        assert new_value == ""  # str()


class TestObjectHolderProperties:
    """Test properties and basic access methods."""

    def test_active_property(self, mock_type_param):
        """Test active property returns current object."""
        holder = StringSpace("test")
        assert holder.active == "test"

    def test_current_property(self, mock_type_param):
        """Test current property returns current pointer."""
        holder = StringSpace()
        assert holder.current == "default"

    def test_names_property(self, mock_type_param):
        """Test names property returns list of keys."""
        holder = StringSpace()
        holder.set("test1", "value1")
        holder.set("test2", "value2")

        names = holder.names
        assert "default" in names
        assert "test1" in names
        assert "test2" in names
        assert len(names) == 3


class TestObjectHolderMethods:
    """Test ObjectHolder methods."""

    def test_has_method(self, mock_type_param):
        """Test has method correctly identifies existing objects."""
        holder = StringSpace()
        assert holder.has("default") is True
        assert holder.has("nonexistent") is False

        holder.set("test", "value")
        assert holder.has("test") is True

    def test_get_existing(self, mock_type_param):
        """Test get method for existing objects."""
        holder = StringSpace("initial")
        holder.set("test", "test_value")

        assert holder.get("default") == "initial"
        assert holder.get("test") == "test_value"

    def test_get_none_returns_current(self, mock_type_param):
        """Test get with None returns current active object."""
        holder = StringSpace("initial")
        assert holder.get(None) == "initial"
        assert holder.get() == "initial"  # No args

    def test_get_nonexistent_creates_new(self, mock_type_param):
        """Test get creates new object for nonexistent names."""
        holder = StringSpace()
        result = holder.get("new_item")

        assert result == ""  # str()
        assert holder.has("new_item") is True
        assert holder.current == "new_item"  # Pointer updated

    def test_set_method(self, mock_type_param):
        """Test set method stores values correctly."""
        holder = StringSpace()
        result = holder.set("test", "test_value")

        assert holder.get("test") == "test_value"
        assert result is holder  # Returns self for chaining

    def test_set_wrong_type_raises_error(self, mock_type_param):
        """Test set with wrong type raises TypeError."""
        holder = StringSpace()
        with pytest.raises(TypeError, match="Value must be of type str"):
            holder.set("test", 123)  # type: ignore[arg-type int instead of str]

    def test_set_active_existing(self, mock_type_param):
        """Test set_active with existing object."""
        holder = StringSpace()
        holder.set("test", "test_value")

        result = holder.set_active("test")
        assert holder.current == "test"
        assert holder.active == "test_value"
        assert result is holder  # Returns self for chaining

    def test_set_active_nonexistent_creates_new(self, mock_type_param):
        """Test set_active creates new object if it doesn't exist."""
        holder = StringSpace()
        holder.set_active("new_item")

        assert holder.current == "new_item"
        assert holder.has("new_item") is True
        assert holder.active == ""  # str()


class TestStringSpace:
    """Test StringSpace specialized functionality."""

    def test_string_space_init(self, mock_type_param):
        """Test StringSpace initialization."""
        space = StringSpace("hello")
        assert space.active == "hello"
        assert isinstance(space.active, str)

    def test_string_space_default_creation(self, mock_type_param):
        """Test StringSpace creates empty strings by default."""
        space = StringSpace()
        space.set_active("new_string")
        assert space.active == ""


class TestBufferSpace:
    """Test BufferSpace specialized functionality."""

    def test_buffer_space_init(self, mock_type_param):
        """Test BufferSpace initialization."""
        buffer = StringIO("initial content")
        space = BufferSpace(buffer)
        assert space.active is buffer

    def test_buffer_space_getvalue(self, mock_type_param):
        """Test BufferSpace getvalue method."""
        space = BufferSpace()
        space.active.write("test content")
        assert space.getvalue() == "test content"

    def test_buffer_space_getvalue_with_name(self, mock_type_param):
        """Test BufferSpace getvalue with specific name."""
        space = BufferSpace()
        space.set_active("test_buffer")
        space.active.write("test content")
        assert space.getvalue("test_buffer") == "test content"

    def test_buffer_space_getvalue_nonexistent_raises_error(self, mock_type_param):
        """Test BufferSpace getvalue with nonexistent buffer raises error."""
        space = BufferSpace()
        with pytest.raises(ValueError, match="No buffer found with name 'nonexistent'"):
            space.getvalue("nonexistent")

    def test_buffer_space_reset(self, mock_type_param):
        """Test BufferSpace reset method."""
        space = BufferSpace()
        space.active.write("test content")
        assert space.getvalue() == "test content"

        result = space.reset()
        assert space.getvalue() == ""
        assert result is space  # Returns self for chaining

    def test_buffer_space_reset_with_name(self, mock_type_param):
        """Test BufferSpace reset with specific name."""
        space = BufferSpace()
        space.set_active("test_buffer")
        space.active.write("test content")

        space.reset("test_buffer")
        assert space.getvalue("test_buffer") == ""


class TestMethodChaining:
    """Test method chaining functionality."""

    def test_fluent_interface(self, mock_type_param):
        """Test that methods return self for chaining."""
        holder = StringSpace()
        result = holder.set("first", "value1").set("second", "value2").set_active("first")

        assert result is holder
        assert holder.current == "first"
        assert holder.active == "value1"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_auto_create_failure(self, mock_type_param):
        """Test behavior when auto-creation fails."""

        # Mock a type that requires arguments
        class RequiresArgs:
            def __init__(self, required_arg):
                self.arg = required_arg

        class TestHolder(ObjectHolder[RequiresArgs]):
            pass

        with patch("bear_utils.extras.utility_classes._holder.type_param", return_value=RequiresArgs):
            holder = TestHolder(RequiresArgs("test"))

            with pytest.raises(TypeError, match="Cannot auto-create RequiresArgs"):
                holder.get("new_item")
