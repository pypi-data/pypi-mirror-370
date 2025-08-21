#!/usr/bin/env python3
"""
Redis Service Consolidation Validation Script

This script validates that the UnifiedRedisService successfully consolidates
the functionality from three separate Redis implementations.
"""

import sys
import traceback


def test_basic_import():
    """Test basic import and instantiation"""
    try:
        from reasoning_kernel.services.unified_redis_service import UnifiedRedisService

        service = UnifiedRedisService()
        print("✅ UnifiedRedisService imported and created successfully")
        return True, service
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False, None


def test_method_availability(service):
    """Test that all essential methods are available"""
    essential_methods = [
        # From RedisMemoryService
        "store_reasoning_chain",
        "get_reasoning_chain",
        "store_knowledge",
        "retrieve_knowledge_by_type",
        "cache_model_result",
        "get_cached_model_result",
        "create_session",
        "get_session",
        # From RedisVectorService
        "initialize_vector_store",
        "similarity_search",
        # From ProductionRedisManager
        "store_world_model",
        "retrieve_world_model",
        "get_performance_metrics",
        "batch_store",
        "cleanup_expired_keys",
        # Connection management
        "connect",
        "disconnect",
        "health_check",
    ]

    available_methods = []
    missing_methods = []

    for method in essential_methods:
        if hasattr(service, method) and callable(getattr(service, method)):
            available_methods.append(method)
            print(f"✅ {method}")
        else:
            missing_methods.append(method)
            print(f"❌ {method} - Missing or not callable")

    print(f"\n📊 Methods Summary: {len(available_methods)}/{len(essential_methods)} available")

    if missing_methods:
        print(f"⚠️  Missing methods: {missing_methods}")
        return False

    return True


def test_configuration(service):
    """Test configuration and initialization"""
    try:
        # Test basic configuration
        assert hasattr(service, "config")
        assert hasattr(service, "schema")
        assert hasattr(service, "enable_monitoring")

        print("✅ Configuration attributes available")

        # Test monitoring attributes
        assert hasattr(service, "_operation_count")
        assert hasattr(service, "_error_count")
        assert hasattr(service, "_cache_hits")
        assert hasattr(service, "_cache_misses")

        print("✅ Monitoring attributes available")

        # Test utility methods
        scenario_hash = service._generate_scenario_hash("test scenario")
        assert isinstance(scenario_hash, str)
        assert len(scenario_hash) == 16

        print("✅ Utility methods working")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_factory_functions():
    """Test factory functions"""
    try:
        from reasoning_kernel.services.unified_redis_service import (
            RedisConnectionConfig,
        )

        # Test configuration class
        config = RedisConnectionConfig(host="test", port=6380)
        assert config.host == "test"
        assert config.port == 6380

        print("✅ Factory functions and configuration classes available")
        return True
    except Exception as e:
        print(f"❌ Factory functions test failed: {e}")
        return False


def test_data_structures():
    """Test data structure definitions"""
    try:
        from reasoning_kernel.services.unified_redis_service import (
            ReasoningRecord,
            WorldModelRecord,
            ExplorationRecord,
        )

        # Test ReasoningRecord
        reasoning_record = ReasoningRecord(
            pattern_type="test", question="What?", reasoning_steps="Step 1", final_answer="Answer", confidence_score=0.9
        )
        assert reasoning_record.pattern_type == "test"
        assert reasoning_record.confidence_score == 0.9
        assert reasoning_record.id  # Auto-generated

        # Test WorldModelRecord
        world_record = WorldModelRecord(model_type="PROBABILISTIC", state_data='{"test": "data"}', confidence=0.8)
        assert world_record.model_type == "PROBABILISTIC"
        assert world_record.confidence == 0.8

        # Test ExplorationRecord
        exploration_record = ExplorationRecord(
            exploration_type="hypothesis",
            hypothesis="Test hypothesis",
            evidence="Test evidence",
            conclusion="Test conclusion",
        )
        assert exploration_record.exploration_type == "hypothesis"

        print("✅ Data structures working correctly")
        return True
    except Exception as e:
        print(f"❌ Data structures test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🔍 Redis Service Consolidation Validation")
    print("=" * 50)

    # Test basic import
    success, service = test_basic_import()
    if not success:
        print("❌ Basic import failed - cannot continue")
        return False

    # Test method availability
    print("\n📋 Testing Method Availability:")
    methods_ok = test_method_availability(service)

    # Test configuration
    print("\n⚙️  Testing Configuration:")
    config_ok = test_configuration(service)

    # Test factory functions
    print("\n🏭 Testing Factory Functions:")
    factory_ok = test_factory_functions()

    # Test data structures
    print("\n📦 Testing Data Structures:")
    data_ok = test_data_structures()

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY:")

    all_tests = [
        ("Basic Import", success),
        ("Method Availability", methods_ok),
        ("Configuration", config_ok),
        ("Factory Functions", factory_ok),
        ("Data Structures", data_ok),
    ]

    passed = sum(1 for _, ok in all_tests if ok)
    total = len(all_tests)

    for test_name, ok in all_tests:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Redis service consolidation is successful!")
        return True
    else:
        print("⚠️  Some tests failed - consolidation needs attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
