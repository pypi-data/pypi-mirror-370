import pytest
from rust_crate_pipeline.common_types import Section, get_section_priority


class TestCommonTypes:
    """Test common_types module."""

    def test_section_creation(self):
        """Test Section creation."""
        section = Section(heading="Test", content="Test content", priority=1)
        assert section["heading"] == "Test"
        assert section["content"] == "Test content"
        assert section["priority"] == 1

    def test_get_section_priority(self):
        """Test get_section_priority function."""
        assert get_section_priority("Usage") == 10
        assert get_section_priority("Features") == 9
        assert get_section_priority("Installation") == 8
        assert get_section_priority("API") == 7
        assert get_section_priority("Other") == 5
