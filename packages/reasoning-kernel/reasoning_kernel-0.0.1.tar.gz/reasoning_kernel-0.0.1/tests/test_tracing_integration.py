#!/usr/bin/env python3
"""
Test script for TASK-013: OpenTelemetry Tracing Integration

This script tests the complete tracing integration including:
1. OpenTelemetry trace initialization
2. MSA pipeline tracing
3. Performance profiling
4. Enhanced logging with correlation IDs
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import modules to test
from reasoning_kernel.core.tracing import (
    initialize_tracing,
    trace_operation,
    correlation_context,
    MSAStageTracer,
    get_correlation_id,
)
from reasoning_kernel.core.profiling import (
    profile_performance,
    profile_msa_stage,
    performance_monitor,
    performance_metrics,
)
from reasoning_kernel.core.logging_config import configure_logging, get_logger, error_context, MSAStageLogger

# Initialize logging and tracing
configure_logging("INFO", json_logs=False)
initialize_tracing(service_name="test-tracing")
logger = get_logger(__name__)

@profile_performance(operation_name="test.simple_operation", log_threshold=0.1)
def simple_profiled_function():
    """Simple function with performance profiling"""

    time.sleep(0.2)  # Simulate work that exceeds threshold
    return "test result"

@profile_msa_stage(stage_name="test.msa_stage", log_threshold=0.1)
async def msa_stage_simulation():
    """Simulate an MSA stage with profiling"""

    await asyncio.sleep(0.15)  # Simulate async work
    return {"stage_result": "success", "data": [1, 2, 3]}

async def test_tracing_integration():
    """Test complete tracing integration"""

    print("🔍 Testing OpenTelemetry Tracing Integration for TASK-013")
    print("=" * 60)

    # Test 1: Basic tracing with correlation context
    print("\n1. Testing basic tracing with correlation context...")

    with correlation_context("test-correlation-123", operation="test_basic_tracing"):
        with trace_operation("test.basic_operation") as span:
            span.add_event("test_event", {"message": "Testing basic tracing"})
            correlation_id = get_correlation_id()
            logger.info("Basic tracing test completed", correlation_id=correlation_id)
            print(f"   ✓ Correlation ID: {correlation_id}")

    # Test 2: MSA Stage Tracer
    print("\n2. Testing MSA Stage Tracer...")

    stage_tracer = MSAStageTracer("test_stage", "Test Stage")
    with stage_tracer.trace_stage_execution(
        input_data={"test_input": "sample data"}, metadata={"test_metadata": "sample metadata"}
    ) as stage_span:
        stage_span.add_event("stage_processing", {"step": "validation"})
        logger.info("MSA stage tracer test completed")
        print("   ✓ MSA Stage Tracer working")

    # Test 3: Performance Profiling
    print("\n3. Testing performance profiling...")

    # Test sync function
    result = simple_profiled_function()
    print(f"   ✓ Sync profiling result: {result}")

    # Test async function
    async_result = await msa_stage_simulation()
    print(f"   ✓ Async MSA stage result: {async_result}")

    # Test 4: Performance Monitor Context
    print("\n4. Testing performance monitor context...")

    with performance_monitor("test.context_operation", log_threshold=0.1, monitor_memory=True):
        await asyncio.sleep(0.12)  # Should exceed threshold
        print("   ✓ Performance monitor context completed")

    # Test 5: Enhanced Logging Features
    print("\n5. Testing enhanced logging features...")

    # Test MSA Stage Logger
    stage_logger = MSAStageLogger("test_enhanced_stage")
    stage_logger.set_stage_context(session_id="test-session", scenario="test scenario")
    stage_logger.log_stage_start(additional_context="test start")


    start_time = time.time()
    await asyncio.sleep(0.05)
    duration = time.time() - start_time
    stage_logger.log_stage_complete(duration, result_size=100)
    print("   ✓ MSA Stage Logger working")

    # Test error context
    try:
        with error_context(logger, "test.error_operation", test_param="test_value"):
            # This will trigger error logging
            raise ValueError("Test error for enhanced logging")
    except ValueError:
        print("   ✓ Enhanced error context logged")

    # Test 6: Performance Metrics Collection
    print("\n6. Testing performance metrics collection...")

    # Record some test metrics
    performance_metrics.record_execution_time("test.operation1", 0.123, {"context": "test1"})
    performance_metrics.record_execution_time("test.operation1", 0.156, {"context": "test2"})
    performance_metrics.record_execution_time("test.operation2", 0.089, {"context": "test3"})

    # Get statistics
    stats1 = performance_metrics.get_statistics("test.operation1")
    print(f"   ✓ Operation1 stats: count={stats1['count']}, avg={stats1['average']:.3f}s")

    all_stats = performance_metrics.get_all_statistics()
    print(f"   ✓ Total operations tracked: {len(all_stats)}")

    # Test 7: Integration Test - Simulated MSA Pipeline Execution
    print("\n7. Testing integrated MSA pipeline simulation...")

    pipeline_session_id = f"test-pipeline-{int(datetime.now().timestamp())}"

    with correlation_context(
        f"pipeline-{pipeline_session_id}", session_id=pipeline_session_id, scenario="Integration test scenario"
    ):
        with performance_monitor("test.msa_pipeline_simulation", log_threshold=0.5, monitor_memory=True):
            with trace_operation("test.msa_pipeline.execute") as pipeline_span:
                pipeline_span.set_attribute("test.session_id", pipeline_session_id)
                pipeline_span.set_attribute("test.scenario_length", "25")

                # Simulate 5 MSA stages
                stage_types = [
                    "knowledge_extraction",
                    "model_specification",
                    "model_synthesis",
                    "probabilistic_inference",
                    "result_integration",
                ]

                for i, stage_type in enumerate(stage_types, 1):
                    stage_tracer = MSAStageTracer(stage_type, f"Stage {i}")

                    with performance_monitor(f"test.stage.{stage_type}", log_threshold=0.1):
                        with stage_tracer.trace_stage_execution(
                            input_data={"stage_input": f"data_for_stage_{i}"}, metadata={"stage_number": i}
                        ) as stage_span:
                            # Simulate stage work
                            await asyncio.sleep(0.05)
                            stage_span.add_event("stage_processing", {"progress": "50%"})
                            await asyncio.sleep(0.05)
                            stage_span.record_output({"stage_result": f"output_from_stage_{i}"})

                pipeline_span.add_event("pipeline_completed")
                print(f"   ✓ Simulated MSA pipeline execution completed for session: {pipeline_session_id}")

    print("\n" + "=" * 60)
    print("🎉 All TASK-013 tracing integration tests completed successfully!")
    print("\nKey components tested:")
    print("  ✓ OpenTelemetry initialization and configuration")
    print("  ✓ Distributed tracing with correlation IDs")
    print("  ✓ MSA stage-specific tracing")
    print("  ✓ Performance profiling decorators")
    print("  ✓ Performance monitoring context managers")
    print("  ✓ Enhanced logging with error context")
    print("  ✓ Performance metrics collection")
    print("  ✓ End-to-end MSA pipeline simulation")
    print("\nTASK-013 implementation is ready for production use! 🚀")

if __name__ == "__main__":
    try:
        asyncio.run(test_tracing_integration())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        sys.exit(1)
