def test_hello():
    """Simple test to verify the test runner works."""
    assert True, "Basic test passed"


def test_import():
    """Test that we can import from our package."""
    from baresquare_sdk import core

    assert core.logger is not None, "Logger module imported successfully"
