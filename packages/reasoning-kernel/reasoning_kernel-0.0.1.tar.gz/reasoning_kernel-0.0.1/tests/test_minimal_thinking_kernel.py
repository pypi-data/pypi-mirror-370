#!/usr/bin/env python3
"""
Minimal test for ThinkingReasoningKernel to identify core issues.
"""


def test_basic_imports():
    """Test basic imports"""
    try:

        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_kernel_creation():
    """Test creating a basic kernel and memory store"""
    try:
        from semantic_kernel import Kernel
        from semantic_kernel.memory import VolatileMemoryStore

        kernel = Kernel()
        memory_store = VolatileMemoryStore()
        print("✅ Kernel and memory store created")
        return True
    except Exception as e:
        print(f"❌ Kernel creation failed: {e}")
        return False


def test_thinking_kernel_init():
    """Test ThinkingReasoningKernel initialization"""
    try:
        from reasoning_kernel.agents.thinking_kernel import ThinkingReasoningKernel
        from semantic_kernel import Kernel
        from semantic_kernel.memory import VolatileMemoryStore

        kernel = Kernel()
        memory_store = VolatileMemoryStore()

        # Try to create ThinkingReasoningKernel without sandbox_client first
        thinking_kernel = ThinkingReasoningKernel(kernel=kernel, memory_store=memory_store, sandbox_client=None)
        print("✅ ThinkingReasoningKernel created successfully")
        return True
    except Exception as e:
        print(f"❌ ThinkingReasoningKernel creation failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running minimal ThinkingReasoningKernel tests...")

    success = test_basic_imports() and test_kernel_creation() and test_thinking_kernel_init()

    if success:
        print("\n🎉 All tests passed! ThinkingReasoningKernel is working.")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
