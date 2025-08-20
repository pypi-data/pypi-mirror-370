"""
Basic test to verify pytest is working.
"""

import pytest


def test_basic():
    """Basic test that should always pass."""
    assert True


def test_import_mcp_security():
    """Test that mcp_security can be imported."""
    try:
        import mcp_security
        assert mcp_security is not None
    except ImportError as e:
        pytest.fail(f"Failed to import mcp_security: {e}")


def test_version():
    """Test that version is available."""
    import mcp_security
    assert hasattr(mcp_security, '__version__')
    assert mcp_security.__version__ == "1.0.0"
