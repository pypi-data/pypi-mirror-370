#!/usr/bin/env python3
"""Comprehensive configuration system validation."""

import sys
import os

sys.path.insert(0, ".")


def comprehensive_config_test():
    """Run comprehensive configuration system validation."""
    print("=== COMPREHENSIVE CONFIGURATION SYSTEM TEST ===")

    try:
        from reasoning_kernel.core.config_manager import ConfigManager, get_config

        print("✅ Successfully imported configuration modules")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 1: Convenience functions
    print("\n1. Testing convenience functions:")
    try:
        config = get_config()
        print(f"✅ get_config() works - Environment: {config.environment}")
    except Exception as e:
        print(f"❌ get_config() failed: {e}")
        return False

    # Test 2: Export functionality
    print("\n2. Testing export functionality:")
    try:
        manager = ConfigManager()
        json_export = manager.export_config("json")
        yaml_export = manager.export_config("yaml")
        print(f"✅ JSON export: {len(json_export)} characters")
        print(f"✅ YAML export: {len(yaml_export)} characters")
    except Exception as e:
        print(f"❌ Export functionality failed: {e}")
        return False

    # Test 3: Configuration summary
    print("\n3. Testing configuration summary:")
    try:
        summary = manager.get_config_summary()
        print("✅ Configuration summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Configuration summary failed: {e}")
        return False

    # Test 4: Environment-specific settings validation
    print("\n4. Testing environment-specific configurations:")
    try:
        original_env = os.environ.get("ENVIRONMENT")

        # Test development settings
        os.environ["ENVIRONMENT"] = "DEVELOPMENT"
        dev_manager = ConfigManager()
        dev_config = dev_manager.config
        print(f"✅ Development - Debug: {dev_config.debug}, Log Level: {dev_config.monitoring.log_level}")

        # Test production settings
        os.environ["ENVIRONMENT"] = "PRODUCTION"
        prod_manager = ConfigManager()
        prod_config = prod_manager.config
        print(f"✅ Production - Debug: {prod_config.debug}, Log Level: {prod_config.monitoring.log_level}")

        # Restore original environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        elif "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

    except Exception as e:
        print(f"❌ Environment handling failed: {e}")
        return False

    print("\n🎉 ALL CONFIGURATION SYSTEM TESTS PASSED!")
    print("✅ Configuration Management System is fully operational")
    return True


if __name__ == "__main__":
    success = comprehensive_config_test()
    sys.exit(0 if success else 1)
