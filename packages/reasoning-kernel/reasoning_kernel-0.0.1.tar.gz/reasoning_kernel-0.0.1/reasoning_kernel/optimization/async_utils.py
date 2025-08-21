"""
Async Request Optimization Utilities

Provides utilities for optimizing async request handling:
- Request batching and deduplication
- Connection pooling optimization
- Concurrent request management
- Response streaming optimization
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, TypeVar
import time
import uuid
from collections import defaultdict
from functools import wraps

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


@dataclass
class BatchRequest:
    """Individual request in a batch"""

    request_id: str
    data: Any
    timestamp: float
    future: asyncio.Future


@dataclass
class BatchConfig:
    """Configuration for request batching"""

    max_batch_size: int = 10
    max_wait_time: float = 0.1  # 100ms
    enabled: bool = True


class RequestBatcher:
    """Batches similar requests together for more efficient processing"""

    def __init__(self, batch_config: BatchConfig = None):
        self.config = batch_config or BatchConfig()
        self.batches: Dict[str, List[BatchRequest]] = defaultdict(list)
        self.batch_timers: Dict[str, asyncio.Task] = {}
        self.processors: Dict[str, Callable] = {}

    def register_processor(self, batch_key: str, processor: Callable[[List[Any]], Awaitable[List[Any]]]):
        """Register a batch processor for a specific batch key"""
        self.processors[batch_key] = processor

    async def add_request(self, batch_key: str, data: Any) -> Any:
        """Add a request to the batch and return the result"""

        if not self.config.enabled:
            # Process immediately if batching disabled
            if batch_key in self.processors:
                results = await self.processors[batch_key]([data])
                return results[0] if results else None
            return None

        request_id = str(uuid.uuid4())
        future = asyncio.Future()

        batch_request = BatchRequest(request_id=request_id, data=data, timestamp=time.time(), future=future)

        self.batches[batch_key].append(batch_request)

        # Start timer if this is the first request in the batch
        if len(self.batches[batch_key]) == 1:
            self.batch_timers[batch_key] = asyncio.create_task(self._batch_timer(batch_key, self.config.max_wait_time))

        # Process immediately if batch is full
        if len(self.batches[batch_key]) >= self.config.max_batch_size:
            await self._process_batch(batch_key)

        # Wait for the result
        return await future

    async def _batch_timer(self, batch_key: str, wait_time: float):
        """Timer to process batch after wait time expires"""
        await asyncio.sleep(wait_time)
        if batch_key in self.batches and self.batches[batch_key]:
            await self._process_batch(batch_key)

    async def _process_batch(self, batch_key: str):
        """Process a batch of requests"""

        if batch_key not in self.batches or not self.batches[batch_key]:
            return

        batch = self.batches[batch_key]
        del self.batches[batch_key]

        # Cancel timer if active
        if batch_key in self.batch_timers:
            self.batch_timers[batch_key].cancel()
            del self.batch_timers[batch_key]

        try:
            if batch_key in self.processors:
                # Extract data from batch requests
                batch_data = [req.data for req in batch]

                logger.info("Processing batch", batch_key=batch_key, size=len(batch_data))

                # Process the batch
                results = await self.processors[batch_key](batch_data)

                # Set results for each future
                for req, result in zip(batch, results):
                    req.future.set_result(result)

            else:
                # No processor registered, return None for all
                for req in batch:
                    req.future.set_result(None)

        except Exception as e:
            logger.error("Batch processing failed", batch_key=batch_key, error=str(e))
            # Set exception for all futures
            for req in batch:
                req.future.set_exception(e)


class ConnectionPool:
    """Manages HTTP connection pooling for external API calls"""

    def __init__(
        self,
        max_connections: int = 100,
        max_connections_per_host: int = 20,
        connection_timeout: float = 10.0,
        read_timeout: float = 30.0,
    ):
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.active_connections: Dict[str, int] = defaultdict(int)
        self.connection_semaphore = asyncio.Semaphore(max_connections)
        self.host_semaphores: Dict[str, asyncio.Semaphore] = {}

    def get_host_semaphore(self, host: str) -> asyncio.Semaphore:
        """Get or create semaphore for specific host"""
        if host not in self.host_semaphores:
            self.host_semaphores[host] = asyncio.Semaphore(self.max_connections_per_host)
        return self.host_semaphores[host]

    @asynccontextmanager
    async def acquire_connection(self, host: str):
        """Acquire connection for specific host"""
        async with self.connection_semaphore:
            async with self.get_host_semaphore(host):
                self.active_connections[host] += 1
                try:
                    yield
                finally:
                    self.active_connections[host] -= 1

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "total_active_connections": sum(self.active_connections.values()),
            "connections_per_host": dict(self.active_connections),
            "available_connections": self.max_connections - sum(self.active_connections.values()),
            "max_connections": self.max_connections,
            "max_per_host": self.max_connections_per_host,
        }


def async_retry(
    max_attempts: int = 3, delay: float = 1.0, backoff_multiplier: float = 2.0, exceptions: tuple = (Exception,)
):
    """Decorator for async functions with exponential backoff retry"""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        # Last attempt, raise the exception
                        raise e

                    # Calculate delay with exponential backoff
                    retry_delay = delay * (backoff_multiplier**attempt)
                    logger.warning(
                        "Function failed, retrying",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=retry_delay,
                        error=str(e),
                    )
                    await asyncio.sleep(retry_delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def async_timeout(timeout_seconds: float):
    """Decorator to add timeout to async functions"""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error("Function timed out", function=func.__name__, timeout=timeout_seconds)
                raise

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for async operations"""

    def __init__(
        self, failure_threshold: int = 5, recovery_timeout: float = 60.0, expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def __call__(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Make circuit breaker callable"""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                # Success - reset failure count
                self._on_success()
                return result

            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        return self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "recovery_timeout": self.recovery_timeout,
        }


class RequestDeduplicator:
    """Deduplicates identical in-flight requests"""

    def __init__(self):
        self.in_flight: Dict[str, asyncio.Future] = {}

    def get_key(self, *args, **kwargs) -> str:
        """Generate key for request deduplication"""
        import hashlib
        import json

        key_data = {"args": str(args), "kwargs": {k: str(v) for k, v in kwargs.items()}}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def deduplicate(self, key: str, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Deduplicate request by key"""

        if key in self.in_flight:
            # Request already in flight, wait for result
            logger.info("Request deduplicated", key=key)
            return await self.in_flight[key]

        # Create new future for this request
        future = asyncio.Future()
        self.in_flight[key] = future

        try:
            # Execute the function
            result = await func(*args, **kwargs)
            future.set_result(result)
            return result

        except Exception as e:
            future.set_exception(e)
            raise

        finally:
            # Remove from in-flight requests
            self.in_flight.pop(key, None)

    def __call__(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Decorator version of deduplicate"""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            key = self.get_key(*args, **kwargs)
            return await self.deduplicate(key, func, *args, **kwargs)

        return wrapper


# Global instances for easy usage
request_batcher = RequestBatcher()
connection_pool = ConnectionPool()
request_deduplicator = RequestDeduplicator()


# Example usage functions
async def batch_llm_calls(inputs: List[str]) -> List[str]:
    """Example batch processor for LLM calls"""
    # This would integrate with your actual LLM service
    logger.info("Processing batch LLM calls", count=len(inputs))

    # Simulate batch processing
    await asyncio.sleep(0.1)  # Simulate API call

    # Return processed results
    return [f"Processed: {inp}" for inp in inputs]


# Register the batch processor
request_batcher.register_processor("llm_calls", batch_llm_calls)


@async_retry(max_attempts=3, delay=1.0)
@async_timeout(30.0)
@request_deduplicator
async def example_api_call(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Example API call with retry, timeout, and deduplication"""

    host = endpoint.split("/")[2]  # Extract host from URL

    async with connection_pool.acquire_connection(host):
        # Simulate API call
        await asyncio.sleep(0.1)
        return {"result": "success", "data": data}
