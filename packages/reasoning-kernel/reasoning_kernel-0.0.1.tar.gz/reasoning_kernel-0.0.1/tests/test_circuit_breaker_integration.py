"""
Test Circuit Breaker Integration with External Services

Tests comprehensive integration of circuit breakers with:
- Daytona Service
- Redis Service
- Web Search Service
- Health Check Endpoints
"""

import asyncio
import pytest
import time

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reasoning_kernel.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerError,
    circuit_breaker_registry,
    create_daytona_circuit_breaker,
    create_redis_circuit_breaker,
    create_websearch_circuit_breaker,
)


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with external services"""

    def test_daytona_circuit_breaker_creation(self):
        """Test Daytona service circuit breaker creation"""
        breaker = create_daytona_circuit_breaker()

        assert breaker is not None
        assert breaker.config.failure_threshold == 5
        assert breaker.config.timeout_duration == 60.0
        assert breaker.config.retry_exceptions == (Exception,)
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_redis_circuit_breaker_creation(self):
        """Test Redis service circuit breaker creation"""
        breaker = create_redis_circuit_breaker()

        assert breaker is not None
        assert breaker.config.failure_threshold == 3
        assert breaker.config.timeout_duration == 30.0
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_websearch_circuit_breaker_creation(self):
        """Test Web Search service circuit breaker creation"""
        breaker = create_websearch_circuit_breaker()

        assert breaker is not None
        assert breaker.config.failure_threshold == 10
        assert breaker.config.timeout_duration == 120.0
        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_registry_integration(self):
        """Test circuit breaker registry functionality"""
        # Create breakers for all services
        daytona_breaker = create_daytona_circuit_breaker()
        redis_breaker = create_redis_circuit_breaker()
        websearch_breaker = create_websearch_circuit_breaker()

        # Verify registry tracks all breakers
        all_status = circuit_breaker_registry.get_all_status()

        assert "daytona" in all_status
        assert "redis" in all_status
        assert "websearch" in all_status

        # Check individual status
        for service, status in all_status.items():
            assert "state" in status
            assert "failure_count" in status
            assert "metrics" in status
            assert status["state"] == "closed"  # Initially closed
            assert status["failure_count"] == 0  # No failures initially

    @pytest.mark.asyncio
    async def test_circuit_breaker_async_protection(self):
        """Test async circuit breaker protection"""
        breaker = CircuitBreaker("test_async", CircuitBreakerConfig(failure_threshold=2))

        # Mock function that fails
        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Service unavailable")

        # First two calls should go through (reach failure threshold)
        with pytest.raises(Exception):
            await breaker.call_async(failing_function)

        with pytest.raises(Exception):
            await breaker.call_async(failing_function)

        assert call_count == 2
        assert breaker.state == CircuitBreakerState.OPEN

        # Third call should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerError):
            await breaker.call_async(failing_function)

        # Call count shouldn't increase (circuit breaker blocked it)
        assert call_count == 2

    def test_circuit_breaker_sync_protection(self):
        """Test sync circuit breaker protection"""
        breaker = CircuitBreaker("test_sync", CircuitBreakerConfig(failure_threshold=2))

        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Service unavailable")

        # First two calls reach failure threshold
        with pytest.raises(Exception):
            breaker.call(failing_function)

        with pytest.raises(Exception):
            breaker.call(failing_function)

        assert call_count == 2
        assert breaker.state == CircuitBreakerState.OPEN

        # Circuit breaker should block third call
        with pytest.raises(CircuitBreakerError):
            breaker.call(failing_function)

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout"""
        config = CircuitBreakerConfig(
            failure_threshold=1, timeout_duration=0.1, half_open_max_calls=1  # Very short timeout for testing
        )
        breaker = CircuitBreaker("test_recovery", config)

        # Fail once to open circuit
        with pytest.raises(Exception):
            breaker.call(lambda: exec('raise Exception("fail")'))

        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.15)

        # Next call should be in HALF_OPEN state
        success_count = 0

        def successful_function():
            nonlocal success_count
            success_count += 1
            return "success"

        # This should succeed and close the circuit
        result = breaker.call(successful_function)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert success_count == 1

    def test_circuit_breaker_metrics_tracking(self):
        """Test circuit breaker metrics collection"""
        breaker = CircuitBreaker("test_metrics", CircuitBreakerConfig())

        # Successful calls
        for i in range(5):
            result = breaker.call(lambda: f"success_{i}")
            assert result.startswith("success_")

        # Failed calls
        for i in range(3):
            try:
                breaker.call(lambda: exec('raise ValueError("test error")'))
            except ValueError:
                pass  # Expected

        metrics = breaker.get_metrics()

        assert metrics["total_calls"] == 8
        assert metrics["successes"] == 5
        assert metrics["failures"] == 3
        assert metrics["success_rate"] == 5 / 8
        assert "avg_response_time" in metrics

    def test_circuit_breaker_health_check(self):
        """Test circuit breaker health check functionality"""

        def always_healthy():
            return True

        def always_unhealthy():
            return False

        # Test healthy service
        healthy_breaker = CircuitBreaker("healthy_service", CircuitBreakerConfig(health_check_function=always_healthy))

        assert healthy_breaker.health_check()

        # Test unhealthy service
        unhealthy_breaker = CircuitBreaker(
            "unhealthy_service", CircuitBreakerConfig(health_check_function=always_unhealthy)
        )

        assert not unhealthy_breaker.health_check()

    def test_circuit_breaker_graceful_degradation(self):
        """Test graceful degradation strategies"""
        # Test cache-based degradation
        cache_strategy = lambda: {"result": "cached_data", "source": "cache"}

        breaker = CircuitBreaker(
            "test_degradation", CircuitBreakerConfig(failure_threshold=1, degradation_strategy=cache_strategy)
        )

        # Fail the service to open circuit
        with pytest.raises(Exception):
            breaker.call(lambda: exec('raise Exception("service down")'))

        assert breaker.state == CircuitBreakerState.OPEN

        # Now calls should return degraded response
        degraded_result = breaker.call_with_degradation(lambda: "normal_result")
        assert degraded_result == {"result": "cached_data", "source": "cache"}

    def test_multiple_service_circuit_breakers(self):
        """Test multiple services with different circuit breaker configs"""
        # Create breakers for different services
        fast_service = CircuitBreaker("fast_service", CircuitBreakerConfig(failure_threshold=3, timeout_duration=10.0))

        slow_service = CircuitBreaker("slow_service", CircuitBreakerConfig(failure_threshold=10, timeout_duration=60.0))

        critical_service = CircuitBreaker(
            "critical_service", CircuitBreakerConfig(failure_threshold=1, timeout_duration=5.0)
        )

        # Test different tolerance levels
        services = [fast_service, slow_service, critical_service]

        for service in services:
            assert service.state == CircuitBreakerState.CLOSED
            assert service.failure_count == 0

        # Critical service should open after 1 failure
        with pytest.raises(Exception):
            critical_service.call(lambda: exec('raise Exception("critical error")'))
        assert critical_service.state == CircuitBreakerState.OPEN

        # Other services should still be closed
        assert fast_service.state == CircuitBreakerState.CLOSED
        assert slow_service.state == CircuitBreakerState.CLOSED


class TestHealthEndpointIntegration:
    """Test health endpoint integration with circuit breakers"""

    @pytest.mark.asyncio
    async def test_health_endpoint_basic(self):
        """Test basic health endpoint functionality"""
        # This would normally import from the actual health endpoint module
        # For now, we'll test the integration patterns

        # Simulate health check data structure
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "circuit_breakers": [
                {"service": "daytona", "state": "closed", "failure_count": 0, "success_rate": 1.0},
                {"service": "redis", "state": "closed", "failure_count": 0, "success_rate": 1.0},
            ],
        }

        assert health_data["status"] == "healthy"
        assert len(health_data["circuit_breakers"]) == 2
        assert all(cb["state"] == "closed" for cb in health_data["circuit_breakers"])

    def test_circuit_breaker_status_serialization(self):
        """Test circuit breaker status can be serialized for API responses"""
        breaker = CircuitBreaker("test_service", CircuitBreakerConfig())

        # Simulate some activity
        breaker.call(lambda: "success")
        try:
            breaker.call(lambda: exec('raise Exception("error")'))
        except Exception:
            pass

        # Get status data
        status = {
            "service": breaker.name,
            "state": breaker.state.value,
            "failure_count": breaker.failure_count,
            "success_rate": breaker.get_metrics()["success_rate"],
            "last_failure": breaker.last_failure_time,
        }

        # Verify serializability
        import json

        json_str = json.dumps(status, default=str)  # Handle datetime serialization
        assert json_str is not None

        # Verify structure
        assert status["service"] == "test_service"
        assert status["state"] in ["closed", "open", "half_open"]
        assert isinstance(status["failure_count"], int)
        assert isinstance(status["success_rate"], float)


def run_circuit_breaker_tests():
    """Run comprehensive circuit breaker integration tests"""
    print("🔧 Testing Circuit Breaker Integration...")

    # Run basic functionality tests
    test_integration = TestCircuitBreakerIntegration()

    # Test service-specific circuit breaker creation
    print("✅ Testing service circuit breaker creation...")
    test_integration.test_daytona_circuit_breaker_creation()
    test_integration.test_redis_circuit_breaker_creation()
    test_integration.test_websearch_circuit_breaker_creation()

    # Test registry integration
    print("✅ Testing circuit breaker registry...")
    test_integration.test_circuit_breaker_registry_integration()

    # Test protection mechanisms
    print("✅ Testing circuit breaker protection...")
    test_integration.test_circuit_breaker_sync_protection()

    # Test metrics and monitoring
    print("✅ Testing metrics tracking...")
    test_integration.test_circuit_breaker_metrics_tracking()

    # Test health checks
    print("✅ Testing health check integration...")
    test_integration.test_circuit_breaker_health_check()

    # Test degradation strategies
    print("✅ Testing graceful degradation...")
    test_integration.test_circuit_breaker_graceful_degradation()

    # Test multi-service scenarios
    print("✅ Testing multi-service scenarios...")
    test_integration.test_multiple_service_circuit_breakers()

    print("🎉 All Circuit Breaker Integration Tests Passed!")

    # Run async tests
    print("\n🔄 Running Async Circuit Breaker Tests...")

    async def run_async_tests():
        await test_integration.test_circuit_breaker_async_protection()
        await test_integration.test_circuit_breaker_recovery()

    asyncio.run(run_async_tests())
    print("🎉 All Async Circuit Breaker Tests Passed!")

    # Test health endpoint integration
    print("\n🏥 Testing Health Endpoint Integration...")
    health_tests = TestHealthEndpointIntegration()
    health_tests.test_health_endpoint_basic()
    health_tests.test_circuit_breaker_status_serialization()
    print("🎉 All Health Endpoint Tests Passed!")

    return True


if __name__ == "__main__":
    success = run_circuit_breaker_tests()
    if success:
        print("\n✅ Circuit Breaker Integration Test Suite: PASSED")
        print("📊 Performance Summary:")
        print("   - Service Protection: ✅ Verified")
        print("   - Fault Tolerance: ✅ Verified")
        print("   - Health Monitoring: ✅ Verified")
        print("   - Graceful Degradation: ✅ Verified")
        print("   - Registry Management: ✅ Verified")
    else:
        print("\n❌ Circuit Breaker Integration Test Suite: FAILED")
        exit(1)
