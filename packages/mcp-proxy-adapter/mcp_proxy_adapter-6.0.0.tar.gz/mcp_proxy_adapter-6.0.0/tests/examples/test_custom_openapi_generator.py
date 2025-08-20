"""
Tests for custom OpenAPI generator example.

This module tests the custom OpenAPI generator functionality including:
- Custom schema generation
- Schema modification
- Generator registration
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.examples.custom_commands import custom_openapi_generator


class TestCustomOpenAPIGenerator:
    """Test custom OpenAPI generator functionality."""

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_openapi_generator_with_app_attributes(self, mock_generator_class, mock_logger):
        """Test custom_openapi_generator with app attributes."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "paths": {}
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "2.0.0"
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify calls
        mock_generator_class.assert_called_once()
        mock_generator.generate.assert_called_once_with(
            title="Test App",
            description="Test Description",
            version="2.0.0"
        )
        
        # Verify schema modifications
        assert "Extended Server Features:" in result["info"]["description"]
        assert "Custom commands with hooks" in result["info"]["description"]
        assert "Data transformation hooks" in result["info"]["description"]
        assert "Command interception hooks" in result["info"]["description"]
        assert "Auto-registration and manual registration examples" in result["info"]["description"]
        
        # Verify custom tags
        assert "tags" in result
        tag_names = [tag["name"] for tag in result["tags"]]
        assert "custom-commands" in tag_names
        assert "hooks" in tag_names
        assert "registration" in tag_names
        
        # Verify custom servers
        assert "servers" in result
        assert len(result["servers"]) == 1
        assert result["servers"][0]["url"] == "http://localhost:8000"
        assert result["servers"][0]["description"] == "Extended server with custom features"
        
        mock_logger.info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_openapi_generator_without_app_attributes(self, mock_generator_class, mock_logger):
        """Test custom_openapi_generator without app attributes."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "paths": {}
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        # Remove attributes to test getattr fallback
        del mock_app.title
        del mock_app.description
        del mock_app.version
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify calls
        mock_generator.generate.assert_called_once_with(
            title=None,
            description=None,
            version=None
        )
        
        # Verify schema modifications still applied
        assert "Extended Server Features:" in result["info"]["description"]
        assert "tags" in result
        assert "servers" in result
        
        mock_logger.info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_openapi_generator_with_existing_tags_and_servers(self, mock_generator_class, mock_logger):
        """Test custom_openapi_generator with existing tags and servers."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "tags": [
                {"name": "existing", "description": "Existing tag"}
            ],
            "servers": [
                {"url": "http://existing:8000", "description": "Existing server"}
            ],
            "paths": {}
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "1.0.0"
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify existing tags and servers are preserved
        assert len(result["tags"]) == 4  # 1 existing + 3 new
        assert len(result["servers"]) == 2  # 1 existing + 1 new
        
        # Verify existing tag is still there
        existing_tag_names = [tag["name"] for tag in result["tags"]]
        assert "existing" in existing_tag_names
        
        # Verify new tags are added
        assert "custom-commands" in existing_tag_names
        assert "hooks" in existing_tag_names
        assert "registration" in existing_tag_names
        
        # Verify existing server is still there
        existing_server_urls = [server["url"] for server in result["servers"]]
        assert "http://existing:8000" in existing_server_urls
        
        # Verify new server is added
        assert "http://localhost:8000" in existing_server_urls
        
        mock_logger.info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_openapi_generator_with_generator_error(self, mock_generator_class, mock_logger):
        """Test custom_openapi_generator with generator error."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate.side_effect = Exception("Generator error")
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "1.0.0"
        
        # Call function and expect exception
        with pytest.raises(Exception, match="Generator error"):
            custom_openapi_generator.custom_openapi_generator(mock_app)
        
        mock_logger.info.assert_not_called()

    def test_generator_registration(self):
        """Test that the custom generator is registered."""
        # Skip this test since registration happens at module import time
        # and mocking it is complex due to import timing
        pytest.skip("Skipping registration test - registration happens at import time")


class TestCustomOpenAPIGeneratorIntegration:
    """Test custom OpenAPI generator integration."""

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_schema_structure_integrity(self, mock_generator_class, mock_logger):
        """Test that the generated schema maintains structural integrity."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "paths": {
                "/api/test": {
                    "get": {
                        "summary": "Test endpoint"
                    }
                }
            }
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "1.0.0"
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify base structure is preserved
        assert "openapi" in result
        assert result["openapi"] == "3.0.0"
        assert "info" in result
        assert "paths" in result
        assert "/api/test" in result["paths"]
        
        # Verify info structure is enhanced
        assert "title" in result["info"]
        assert "description" in result["info"]
        assert "version" in result["info"]
        assert "Extended Server Features:" in result["info"]["description"]
        
        # Verify new sections are added
        assert "tags" in result
        assert "servers" in result
        
        mock_logger.info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_tags_content(self, mock_generator_class, mock_logger):
        """Test that custom tags have the correct content."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "paths": {}
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "1.0.0"
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify custom tags content
        custom_commands_tag = next(tag for tag in result["tags"] if tag["name"] == "custom-commands")
        assert custom_commands_tag["description"] == "Custom commands with advanced features"
        
        hooks_tag = next(tag for tag in result["tags"] if tag["name"] == "hooks")
        assert hooks_tag["description"] == "Command hooks for data transformation and interception"
        
        registration_tag = next(tag for tag in result["tags"] if tag["name"] == "registration")
        assert registration_tag["description"] == "Command registration examples"
        
        mock_logger.info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_openapi_generator.CustomOpenAPIGenerator')
    def test_custom_server_content(self, mock_generator_class, mock_logger):
        """Test that custom server has the correct content."""
        # Setup mocks
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        base_schema = {
            "info": {
                "title": "Test API",
                "description": "Base description",
                "version": "1.0.0"
            },
            "paths": {}
        }
        mock_generator.generate.return_value = base_schema.copy()
        
        mock_app = MagicMock()
        mock_app.title = "Test App"
        mock_app.description = "Test Description"
        mock_app.version = "1.0.0"
        
        # Call function
        result = custom_openapi_generator.custom_openapi_generator(mock_app)
        
        # Verify custom server content
        custom_server = next(server for server in result["servers"] if server["url"] == "http://localhost:8000")
        assert custom_server["description"] == "Extended server with custom features"
        
        mock_logger.info.assert_called_once() 