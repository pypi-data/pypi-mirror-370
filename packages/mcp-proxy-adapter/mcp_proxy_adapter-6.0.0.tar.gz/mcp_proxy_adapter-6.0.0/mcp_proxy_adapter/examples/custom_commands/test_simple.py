#!/usr/bin/env python3
"""
Simple test in custom_commands directory.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

print("1. Importing registry directly...")
from mcp_proxy_adapter.commands.command_registry import registry
print(f"   Registry has reload_system: {hasattr(registry, 'reload_system')}")

print("2. Testing reload_system...")
try:
    result = registry.reload_system()
    print(f"   ✅ reload_system worked: {result}")
except Exception as e:
    print(f"   ❌ reload_system failed: {e}") 