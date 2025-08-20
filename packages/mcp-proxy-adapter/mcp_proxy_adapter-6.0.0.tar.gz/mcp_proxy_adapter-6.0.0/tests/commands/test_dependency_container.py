"""
Tests for dependency container module.
"""

import pytest

from mcp_proxy_adapter.commands.dependency_container import DependencyContainer


class TestDependencyContainer:
    """Tests for DependencyContainer class."""

    def test_register_and_get(self):
        """Test registering and retrieving dependencies."""
        container = DependencyContainer()
        test_dependency = {"key": "value"}
        
        # Register and retrieve dependency
        container.register("test", test_dependency)
        retrieved = container.get("test")
        
        assert retrieved is test_dependency
        assert container.has("test")
        
    def test_register_factory(self):
        """Test registering and using factory function."""
        container = DependencyContainer()
        
        # Create a factory that returns a new dict each time
        factory_calls = 0
        
        def factory():
            nonlocal factory_calls
            factory_calls += 1
            return {"instance": factory_calls}
            
        container.register_factory("factory_test", factory)
        
        # Each call should create a new instance
        first = container.get("factory_test")
        second = container.get("factory_test")
        
        assert first != second
        assert first["instance"] == 1
        assert second["instance"] == 2
        assert factory_calls == 2
        assert container.has("factory_test")
        
    def test_register_singleton(self):
        """Test registering and using singleton factory."""
        container = DependencyContainer()
        
        # Create a factory that counts calls
        factory_calls = 0
        
        def factory():
            nonlocal factory_calls
            factory_calls += 1
            return {"instance": factory_calls}
            
        container.register_singleton("singleton_test", factory)
        
        # First call should create instance
        first = container.get("singleton_test")
        # Second call should return the same instance
        second = container.get("singleton_test")
        
        assert first is second
        assert first["instance"] == 1
        assert factory_calls == 1
        assert container.has("singleton_test")
        
    def test_get_nonexistent(self):
        """Test getting a non-registered dependency."""
        container = DependencyContainer()
        
        with pytest.raises(KeyError):
            container.get("nonexistent")
            
        assert not container.has("nonexistent")
        
    def test_clear(self):
        """Test clearing all dependencies."""
        container = DependencyContainer()
        
        container.register("test1", "value1")
        container.register_factory("test2", lambda: "value2")
        container.register_singleton("test3", lambda: "value3")
        
        # Get singleton to create it
        container.get("test3")
        
        # Clear all
        container.clear()
        
        assert not container.has("test1")
        assert not container.has("test2")
        assert not container.has("test3")
        
        with pytest.raises(KeyError):
            container.get("test1") 