"""Test german-protest-registrations."""

import german_protest_registrations


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(german_protest_registrations.__name__, str)
