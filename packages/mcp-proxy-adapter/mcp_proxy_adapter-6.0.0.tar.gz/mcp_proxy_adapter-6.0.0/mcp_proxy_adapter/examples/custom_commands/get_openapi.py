#!/usr/bin/env python3
"""
Script to get OpenAPI schema directly from the code.
"""

import json
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

from mcp_proxy_adapter.custom_openapi import CustomOpenAPIGenerator
from mcp_proxy_adapter.commands.command_registry import registry

async def main():
    """Generate and save OpenAPI schema."""
    try:
        # Initialize commands first
        print("🔄 Initializing commands...")
        result = await registry.reload_system()
        print(f"✅ Commands initialized: {result}")
        
        # Load custom commands manually
        print("🔄 Loading custom commands...")
        custom_commands = [
            "echo_command",
            "custom_help_command", 
            "custom_health_command",
            "manual_echo_command"
        ]
        
        for cmd_name in custom_commands:
            try:
                # Import the command module
                module = __import__(cmd_name)
                print(f"✅ Loaded custom command: {cmd_name}")
                
                # Try to register the command if it has a command class
                if hasattr(module, 'EchoCommand'):
                    registry.register_custom(module.EchoCommand())
                    print(f"✅ Registered EchoCommand")
                elif hasattr(module, 'CustomHelpCommand'):
                    registry.register_custom(module.CustomHelpCommand())
                    print(f"✅ Registered CustomHelpCommand")
                elif hasattr(module, 'CustomHealthCommand'):
                    registry.register_custom(module.CustomHealthCommand())
                    print(f"✅ Registered CustomHealthCommand")
                elif hasattr(module, 'ManualEchoCommand'):
                    registry.register_custom(module.ManualEchoCommand())
                    print(f"✅ Registered ManualEchoCommand")
                    
            except Exception as e:
                print(f"⚠️ Failed to load {cmd_name}: {e}")
        
        # Get commands after registration
        print("📋 Getting commands after registration...")
        commands = registry.get_all_commands()
        print(f"   Total commands: {len(commands)}")
        print(f"   Command names: {list(commands.keys())}")
        
        # Create generator
        generator = CustomOpenAPIGenerator()
        
        # Generate schema
        schema = generator.generate(
            title="Extended MCP Proxy Server",
            description="Advanced MCP Proxy Adapter server with custom commands and hooks",
            version="2.1.0"
        )
        
        # Save to file
        with open("generated_openapi.json", "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print("✅ OpenAPI schema generated successfully!")
        print(f"📄 Saved to: generated_openapi.json")
        print(f"📊 Schema size: {len(json.dumps(schema))} characters")
        
        # Show basic info
        print(f"\n📋 Schema info:")
        print(f"   Title: {schema['info']['title']}")
        print(f"   Version: {schema['info']['version']}")
        
        # Get commands info
        commands = registry.get_all_commands()
        print(f"   Commands: {len(commands)}")
        print(f"   Command names: {list(commands.keys())}")
        
        # Check CommandRequest enum
        command_enum = schema['components']['schemas'].get('CommandRequest', {}).get('properties', {}).get('command', {}).get('enum', [])
        print(f"   Commands in schema: {len(command_enum)}")
        print(f"   Schema commands: {command_enum}")
        
    except Exception as e:
        print(f"❌ Error generating schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 