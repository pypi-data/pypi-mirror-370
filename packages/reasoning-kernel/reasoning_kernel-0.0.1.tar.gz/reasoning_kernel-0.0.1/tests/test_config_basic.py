#!/usr/bin/env python3
"""Basic configuration system validation test."""

import sys
import os

sys.path.insert(0, ".")


def test_config_system():
    """Test basic configuration system functionality."""
    try:
        from reasoning_kernel.core.config_manager import ApplicationConfig, ConfigManager

        print("✅ Successfully imported configuration modules")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 1: Basic ApplicationConfig creation
    print("\nTest 1: ApplicationConfig creation")
    try:
        config = ApplicationConfig()
        print("✅ ApplicationConfig created successfully")
        print(f"   Environment: {config.environment}")
        print(f"   Debug mode: {config.debug}")
        print(f"   Log level: {config.monitoring.log_level}")
        print(f"   Azure OpenAI timeout: {config.azure_openai.timeout}")
        print(f"   Redis max connections: {config.redis.max_connections}")
    except Exception as e:
        print(f"❌ ApplicationConfig creation failed: {e}")
        return False

    # Test 2: ConfigManager initialization
    print("\nTest 2: ConfigManager initialization")
    try:
        manager = ConfigManager()
        print("✅ ConfigManager created successfully")
        config_from_manager = manager.config
        print(f"   Loaded environment: {config_from_manager.environment}")
        print(f"   Config path: {manager.config_path}")
    except Exception as e:
        print(f"❌ ConfigManager creation failed: {e}")
        return False

    # Test 3: Configuration summary
    print("\nTest 3: Configuration summary")
    try:
        summary = manager.get_config_summary()
        print(f"✅ Config summary generated: {len(summary)} fields")
        print("   Summary details:")
        for i, (key, value) in enumerate(summary.items()):
            print(f"     {i+1}. {key}: {value}")
            if i >= 4:  # Show first 5 items
                print(f"     ... and {len(summary) - 5} more fields")
                break
    except Exception as e:
        print(f"❌ Config summary failed: {e}")
        return False

    # Test 4: Environment-specific configuration
    print("\nTest 4: Environment handling")
    try:
        # Test development environment
        os.environ["ENVIRONMENT"] = "DEVELOPMENT"
        dev_config = ApplicationConfig()
        print(f"✅ Development config: debug={dev_config.debug}, log_level={dev_config.monitoring.log_level}")

        # Test production environment
        os.environ["ENVIRONMENT"] = "PRODUCTION"
        prod_config = ApplicationConfig()
        print(f"✅ Production config: debug={prod_config.debug}, log_level={prod_config.monitoring.log_level}")

        # Reset to default
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

    except Exception as e:
        print(f"❌ Environment handling failed: {e}")
        return False

    print("\n🎉 All configuration system tests passed successfully!")
    return True


if __name__ == "__main__":
    success = test_config_system()
    sys.exit(0 if success else 1)
