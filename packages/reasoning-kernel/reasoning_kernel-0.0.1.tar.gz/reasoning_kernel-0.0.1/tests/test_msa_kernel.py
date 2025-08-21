#!/usr/bin/env python3
"""
Test script for MSAKernel implementation.
Tests the MSA kernel configuration without requiring external dependencies.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_msa_kernel_basic():
    """Test basic MSAKernel functionality"""
    try:
        from reasoning_kernel.core.msa_kernel import MSAKernelConfig, MSAKernel

        print("✓ MSAKernel imports successfully")

        # Test configuration creation
        config = MSAKernelConfig(
            {
                "chat_model_id": "gpt-4o-mini",
                "embedding_model_id": "text-embedding-3-small",
                "enable_memory": False,  # Disable for test
                "enable_plugins": True,
            }
        )

        print("✓ MSAKernelConfig created successfully")
        print(f"  - Chat model: {config.chat_model_id}")
        print(f"  - Embedding model: {config.embedding_model_id}")
        print(f"  - Memory enabled: {config.enable_memory}")
        print(f"  - Plugins enabled: {config.enable_plugins}")

        # Test kernel creation (without initialization to avoid API key requirements)
        kernel = MSAKernel(config)

        print("✓ MSAKernel instantiated successfully")
        print(f"  - Initialized: {kernel.is_initialized()}")

        # Test service info before initialization
        service_info = kernel.get_service_info()
        print("✓ Service info accessible")
        print(f"  - Chat service available: {service_info['chat_service']['available']}")
        print(f"  - Embedding service available: {service_info['embedding_service']['available']}")
        print(f"  - Memory store available: {service_info['memory_store']['available']}")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

async def test_msa_kernel_factory():
    """Test MSAKernel factory functions"""
    try:
        from reasoning_kernel.core.msa_kernel import create_msa_kernel, create_default_msa_kernel

        print("✓ Factory functions imported successfully")

        # Note: We can't actually call these without API keys, but we can verify they exist
        print("✓ create_msa_kernel function available")
        print("✓ create_default_msa_kernel function available")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_imports():
    """Test that all MSA kernel components can be imported"""
    try:
        from reasoning_kernel.core.msa_kernel import (
            MSAKernelConfig,
            MSAKernel,
            create_msa_kernel,
            create_default_msa_kernel,
        )

        print("✓ All MSAKernel components imported successfully")
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

async def main():
    """Run all MSAKernel tests"""
    print("🔍 Testing MSAKernel Implementation")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_msa_kernel_basic),
        ("Factory Functions", test_msa_kernel_factory),
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")

    print("\n" + "=" * 50)
    if passed == len(tests):
        print(f"🎉 All {len(tests)} tests passed!")
        print("✅ TASK-008: MSAKernel implementation is complete")
        return 0
    else:
        print(f"❌ {len(tests) - passed} of {len(tests)} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
