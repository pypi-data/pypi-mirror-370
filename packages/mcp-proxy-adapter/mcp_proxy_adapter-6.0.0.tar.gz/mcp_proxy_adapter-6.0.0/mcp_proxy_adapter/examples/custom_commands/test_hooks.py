"""
Test Hooks Example

This script demonstrates the hooks system by making requests to the server
and showing how hooks process the commands.
"""

import requests
import json
import time


def test_echo_hooks():
    """Test echo command with hooks."""
    print("\n🔔 Testing Echo Command with Hooks")
    print("=" * 50)
    
    # Test basic echo
    response = requests.post(
        "http://localhost:8000/cmd",
        json={
            "command": "echo",
            "params": {"message": "Hello from hooks!"}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Echo command executed successfully")
        print(f"📤 Result: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def test_help_hooks():
    """Test help command with hooks."""
    print("\n📖 Testing Help Command with Hooks")
    print("=" * 50)
    
    # Test help for all commands
    response = requests.post(
        "http://localhost:8000/cmd",
        json={"command": "help"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Help command executed successfully")
        print(f"📚 Total commands: {result.get('total', 0)}")
        print(f"🔧 Custom features: {result.get('custom_features', {})}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    # Test help for specific command
    response = requests.post(
        "http://localhost:8000/cmd",
        json={
            "command": "help",
            "params": {"cmdname": "echo"}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Help for echo command executed successfully")
        print(f"📖 Command info: {result.get('info', {}).get('description', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def test_health_hooks():
    """Test health command with hooks."""
    print("\n🏥 Testing Health Command with Hooks")
    print("=" * 50)
    
    response = requests.post(
        "http://localhost:8000/cmd",
        json={"command": "health"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Health command executed successfully")
        
        data = result.get("data", {})
        print(f"🏥 Status: {data.get('status', 'unknown')}")
        print(f"⏱️  Uptime: {data.get('uptime', 0):.2f}s")
        
        custom_metrics = data.get("custom_metrics", {})
        print(f"🔧 Hook enhanced: {custom_metrics.get('hook_enhanced', False)}")
        print(f"🆔 Health check ID: {custom_metrics.get('health_check_id', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def test_security_hooks():
    """Test security hooks with sensitive data."""
    print("\n🔒 Testing Security Hooks")
    print("=" * 50)
    
    # Test with sensitive parameter
    response = requests.post(
        "http://localhost:8000/cmd",
        json={
            "command": "echo",
            "params": {
                "message": "Test message",
                "password": "secret123",
                "api_token": "sensitive_data"
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Echo command with sensitive data executed")
        print("🔒 Security hooks should have logged warnings")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def test_performance_hooks():
    """Test performance hooks with slow operation simulation."""
    print("\n⏱️  Testing Performance Hooks")
    print("=" * 50)
    
    # Test with a command that might be slow
    response = requests.post(
        "http://localhost:8000/cmd",
        json={
            "command": "health",
            "params": {}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Health command executed")
        print("⏱️  Performance hooks should have logged execution time")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


def main():
    """Run all hook tests."""
    print("🧪 Testing Custom Commands with Hooks")
    print("=" * 60)
    print("Make sure the server is running on http://localhost:8000")
    print("Check the server logs to see hook activity")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    try:
        test_echo_hooks()
        test_help_hooks()
        test_health_hooks()
        test_security_hooks()
        test_performance_hooks()
        
        print("\n✅ All tests completed!")
        print("📋 Check the server logs to see hook activity:")
        print("   - Command-specific hooks")
        print("   - Global hooks")
        print("   - Performance monitoring")
        print("   - Security monitoring")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")


if __name__ == "__main__":
    main() 