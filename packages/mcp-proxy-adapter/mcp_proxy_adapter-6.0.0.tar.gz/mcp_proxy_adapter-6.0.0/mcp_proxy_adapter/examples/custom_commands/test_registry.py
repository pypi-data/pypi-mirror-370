#!/usr/bin/env python3
"""
Test script to understand registry issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

print("1. Importing registry directly...")
from mcp_proxy_adapter.commands.command_registry import registry
print(f"   Registry type: {type(registry)}")
print(f"   Registry has reload_system: {hasattr(registry, 'reload_system')}")
print(f"   Registry methods: {[m for m in dir(registry) if not m.startswith('_')]}")

print("2. Testing reload_system...")
try:
    result = registry.reload_system()
    print(f"   ✅ reload_system worked: {result}")
except Exception as e:
    print(f"   ❌ reload_system failed: {e}")
    import traceback
    traceback.print_exc() 