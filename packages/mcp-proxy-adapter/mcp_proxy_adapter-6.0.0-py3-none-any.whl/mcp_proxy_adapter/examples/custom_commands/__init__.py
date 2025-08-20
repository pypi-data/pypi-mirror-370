"""
Custom Commands Example

An example of MCP Proxy Adapter server with custom commands:
- echo command
- custom help command
- custom health command
"""

__version__ = "1.0.0"

# Import all modules to make them available
from . import echo_command
from . import custom_help_command
from . import custom_health_command
from . import manual_echo_command
from . import intercept_command
from . import data_transform_command
from . import advanced_hooks
from . import hooks
from . import custom_settings_manager
from . import custom_openapi_generator
# Server import removed to avoid circular imports

# Import auto commands
from .auto_commands import auto_echo_command
from .auto_commands import auto_info_command 