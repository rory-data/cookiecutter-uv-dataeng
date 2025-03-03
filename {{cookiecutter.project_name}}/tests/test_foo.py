"""Tests for the foo module."""

import pytest
from include.foo import foo


def test_foo() -> None:
    """Test that the foo function returns its input correctly."""
    result = foo("foo")
    pytest.assume(result == "foo")
