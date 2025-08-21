import asyncio
import time

from reasoning_kernel.optimization import TTLCache, LRUCache, AdaptiveCache, memoize_async, InflightDeduper


def test_ttl_cache_basic():
    c = TTLCache(default_ttl=0.1)
    assert c.get("x") is None
    c.set("x", 42)
    assert c.get("x") == 42
    time.sleep(0.12)
    assert c.get("x") is None


def test_lru_cache_eviction_and_ttl():
    c = LRUCache(maxsize=2, default_ttl=0.5)
    c.set("a", 1)
    c.set("b", 2)
    # fill and access a to make b LRU
    assert c.get("a") == 1
    c.set("c", 3)
    # b should be evicted
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3


async def _slow_add(a, b, delay=0.05):
    await asyncio.sleep(delay)
    return a + b


def test_adaptive_cache_promote_event_loop():
    c = AdaptiveCache(lru_size=1, ttl_default=1.0)
    assert c.get("k") is None
    c.set("k", 7)
    # first from lru after set
    assert c.get("k") == 7
    # fallback path: set directly into ttl, then access via ttl, promotion to lru
    c._lru.clear()
    assert c.get("k") == 7


def test_memoize_async_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    cache = AdaptiveCache()

    @memoize_async(cache, key_fn=lambda a, b: (a, b))
    async def add(a, b):
        return await _slow_add(a, b)

    t0 = time.time()
    v1 = loop.run_until_complete(add(2, 3))
    t1 = time.time()
    v2 = loop.run_until_complete(add(2, 3))
    t2 = time.time()

    assert v1 == 5 and v2 == 5
    assert (t2 - t1) < (t1 - t0)  # cached second run faster

    loop.close()


def test_inflight_deduper():
    async def work(x):
        await asyncio.sleep(0.05)
        return x * 2

    deduper = InflightDeduper[str, int]()

    async def run_parallel():
        async def factory():
            return await work(3)

        # launch 3 concurrent same-key tasks
        results = await asyncio.gather(
            deduper.run("k", factory),
            deduper.run("k", factory),
            deduper.run("k", factory),
        )
        return results

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_parallel())
    loop.close()

    assert results == [6, 6, 6]
