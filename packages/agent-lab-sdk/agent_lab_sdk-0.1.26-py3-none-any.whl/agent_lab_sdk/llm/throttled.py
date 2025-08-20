import os
import asyncio
import threading
import time
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat import GigaChatEmbeddings
import langchain_gigachat.embeddings.gigachat

langchain_gigachat.embeddings.gigachat.MAX_BATCH_SIZE_PARTS=int(os.getenv("EMBEDDINGS_MAX_BATCH_SIZE_PARTS", "90"))

MAX_CHAT_CONCURRENCY = int(os.getenv("MAX_CHAT_CONCURRENCY", "100000"))
MAX_EMBED_CONCURRENCY = int(os.getenv("MAX_EMBED_CONCURRENCY", "100000"))


from agent_lab_sdk.metrics import get_metric

def create_metrics(prefix: str):
    in_use = get_metric(
        metric_type = "gauge", name = f"{prefix}_slots_in_use",
        documentation = f"Number of {prefix} slots currently in use"
    )
    waiting = get_metric(
        metric_type = "gauge", name = f"{prefix}_waiting_tasks",
        documentation = f"Number of tasks waiting for {prefix}"
    )
    wait_time = get_metric(
        metric_type = "histogram", name = f"{prefix}_wait_time_seconds",
        documentation = f"Time tasks wait for {prefix}",
        buckets = [3, 5, 10, 15, 30, 60, 120, 240, 480, 960, 1920, float("inf")]
    )

    return in_use, waiting, wait_time

chat_in_use, chat_waiting, chat_wait_hist = create_metrics("chat")
embed_in_use, embed_waiting, embed_wait_hist = create_metrics("embed")

class UnifiedSemaphore:
    """Threading-based семафор + sync/async API + metrics + контекстники."""
    def __init__(self, limit, in_use, waiting, wait_hist):
        self._sem       = threading.Semaphore(limit)
        self._limit     = limit
        self._in_use    = in_use
        self._waiting   = waiting
        self._wait_hist = wait_hist
        self._current   = 0

        self._in_use.set(0)
        self._waiting.set(0)

    # ——— синхронный API ———
    def acquire(self):
        self._waiting.inc()
        start = time.time()

        self._sem.acquire()
        elapsed = time.time() - start
        self._wait_hist.observe(elapsed)
        self._waiting.dec()

        self._current += 1
        self._in_use.set(self._current)

    def release(self):
        self._sem.release()
        self._current -= 1
        self._in_use.set(self._current)

    # контекстник для sync
    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

    # ——— асинхронный API ———
    async def acquire_async(self):
        self._waiting.inc()
        start = time.time()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sem.acquire)
        elapsed = time.time() - start
        self._wait_hist.observe(elapsed)
        self._waiting.dec()

        self._current += 1
        self._in_use.set(self._current)

    async def release_async(self):
        # release очень быстрый
        self._sem.release()
        self._current -= 1
        self._in_use.set(self._current)

    # контекстник для async
    async def __aenter__(self):
        await self.acquire_async()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.release_async()

# Semaphores for chat and embeddings
_semaphores = {
    "chat": UnifiedSemaphore(MAX_CHAT_CONCURRENCY, chat_in_use, chat_waiting, chat_wait_hist),
    "embed": UnifiedSemaphore(MAX_EMBED_CONCURRENCY, embed_in_use, embed_waiting, embed_wait_hist),
}

class ThrottledGigaChatEmbeddings(GigaChatEmbeddings):
    def embed_documents(self, *args, **kwargs):
        with _semaphores["embed"]:
            return super().embed_documents(*args, **kwargs)

    def embed_query(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызвается embed_documents, семафор уже там
        return super().embed_query(*args, **kwargs)

    async def aembed_documents(self, *args, **kwargs):
        async with _semaphores["embed"]:
            return await super().aembed_documents(*args, **kwargs)

    async def aembed_query(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызвается aembed_documents, семафор уже там
        return await super().aembed_query(*args, **kwargs)

# по хорошему бы переопределять клиент гигачата или манкипатчить его, но это не так просто
class ThrottledGigaChat(GigaChat):
    def invoke(self, *args, **kwargs):
        with _semaphores["chat"]:
            return super().invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        async with _semaphores["chat"]:
            return await super().ainvoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        if super()._should_stream(async_api=False, **{**kwargs, "stream": True}):
            with _semaphores["chat"]:
                for chunk in super().stream(*args, **kwargs):
                    yield chunk
        else:
            # здесь есть проблема когда внутри stream вызывается invoke, поэтому без семафора
            for chunk in super().stream(*args, **kwargs):
                    yield chunk

    async def astream(self, *args, **kwargs):
        if super()._should_stream(async_api=True, **{**kwargs, "stream": True}):
            async with _semaphores["chat"]:
                async for chunk in super().astream(*args, **kwargs):
                    yield chunk
        else:
            # здесь есть проблема когда внутри stream вызывается ainvoke, поэтому без семафора
            async for chunk in super().astream(*args, **kwargs):
                yield chunk

    async def astream_events(self, *args, **kwargs):
        async with _semaphores["chat"]:
            async for ev in super().astream_events(*args, **kwargs):
                yield ev

    def batch(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызывается invoke, семафор уже там
        return super().batch(*args, **kwargs)

    async def abatch(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызывается ainvoke, семафор уже там
        return await super().abatch(*args, **kwargs)

    def batch_as_completed(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызывается invoke, семафор уже там
        for item in super().batch_as_completed(*args, **kwargs):
            yield item

    async def abatch_as_completed(self, *args, **kwargs):
        # здесь семафор не нужен, под капотом вызывается ainvoke, семафор уже там
        async for item in super().abatch_as_completed(*args, **kwargs):
            yield item
