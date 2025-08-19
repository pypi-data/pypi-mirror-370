import pytest
from rust_crate_pipeline.utils.serialization_utils import to_serializable
from unittest.mock import Mock, MagicMock


class TestSerializationUtils:
    """Test serialization_utils module."""

    def test_to_serializable_primitives(self):
        """Test to_serializable with primitive types."""
        assert to_serializable(1) == 1
        assert to_serializable(1.0) == 1.0
        assert to_serializable("test") == "test"
        assert to_serializable(True) is True
        assert to_serializable(None) is None

    def test_to_serializable_collections(self):
        """Test to_serializable with collections."""
        assert to_serializable([1, 2, 3]) == [1, 2, 3]
        assert to_serializable((1, 2, 3)) == [1, 2, 3]
        assert to_serializable({1, 2, 3}) == [1, 2, 3]
        assert to_serializable({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_to_serializable_objects(self):
        """Test to_serializable with objects."""

        class TestObject:
            def to_dict(self):
                return {"a": 1}

        assert to_serializable(TestObject()) == {"a": 1}

    def test_to_serializable_mock(self):
        """Test to_serializable with a mock object."""
        mock_object = MagicMock()
        mock_object.to_dict.return_value = {"a": 1}
        assert to_serializable(mock_object) == {"a": 1}
