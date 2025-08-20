import pytest
import asyncio
import time
from wove import weave


@pytest.mark.asyncio
async def test_basic_mapping():
    """Tests that a task can be mapped over a simple iterable."""
    items = [1, 2, 3]
    async with weave() as w:

        @w.do(items)
        async def process_item(item):
            await asyncio.sleep(0.01)
            return item * 2

    assert w.result["process_item"] == [2, 4, 6]


@pytest.mark.asyncio
async def test_mapping_with_dependency():
    """Tests that a mapped task can depend on another task."""
    items = [10, 20]
    async with weave() as w:

        @w.do
        def multiplier():
            return 3

        @w.do(items)
        def process_item_with_dep(item, multiplier):
            return item * multiplier

    assert w.result["process_item_with_dep"] == [30, 60]


@pytest.mark.asyncio
async def test_mapping_over_empty_list():
    """Tests that mapping over an empty list produces an empty list and does not run the function."""
    was_called = False
    async with weave() as w:

        @w.do([])
        def process_item(item):
            nonlocal was_called
            was_called = True
            # This should never run
            return item * 2

    assert w.result["process_item"] == []
    assert not was_called, "Mapped function should not be called for an empty iterable."


@pytest.mark.asyncio
async def test_sync_function_mapping():
    """Tests mapping over an iterable with a synchronous function."""
    items = [0.01, 0.01, 0.01]
    start_time = time.time()
    async with weave() as w:

        @w.do(items)
        def sync_process(item):
            time.sleep(item)
            return True

    duration = time.time() - start_time
    # If run in series, would be > 0.03. Concurrently in threads, should be less.
    assert duration < 0.025
    assert w.result["sync_process"] == [True, True, True]


@pytest.mark.asyncio
async def test_downstream_task_uses_mapped_results():
    """Tests that a subsequent task can use the collected results of a mapped task."""
    items = [1, 2, 3]
    async with weave() as w:

        @w.do(items)
        def square(item):
            return item * item

        @w.do
        def sum_squares(square):
            return sum(square)

    assert w.result["sum_squares"] == 14  # 1 + 4 + 9
    assert w.result["square"] == [1, 4, 9]


@pytest.mark.asyncio
async def test_mapped_task_signature_validation():
    """Tests that a mapped task with an incorrect signature raises a TypeError."""
    with pytest.raises(
        TypeError, match="must have exactly one parameter that is not a dependency"
    ):
        async with weave() as w:

            @w.do([1, 2, 3])
            def no_item_param():
                return 1

    with pytest.raises(
        TypeError, match="must have exactly one parameter that is not a dependency"
    ):
        async with weave() as w:

            @w.do
            def some_dep():
                return 5

            @w.do([1, 2, 3])
            def too_many_params(item1, item2, some_dep):
                return item1 + item2 + some_dep


@pytest.mark.asyncio
async def test_fundamental_mapping():
    """Tests that decorating a function with @w.do([1, 2, 3]) executes it for each item."""
    async with weave() as w:

        @w.do([1, 2, 3])
        def process(item):
            return item * 2

    assert w.result["process"] == [2, 4, 6]


@pytest.mark.asyncio
async def test_mapping_with_async_dependency():
    """Tests that a mapped task can depend on a preceding, non-mapped, async task."""
    items = [10, 20]
    async with weave() as w:

        @w.do
        async def multiplier():
            await asyncio.sleep(0.01)
            return 3

        @w.do(items)
        def process_item_with_dep(item, multiplier):
            return item * multiplier

    assert w.result["process_item_with_dep"] == [30, 60]


@pytest.mark.asyncio
async def test_async_downstream_task_uses_mapped_results():
    """Tests an async downstream task using async mapped results."""
    items = [1, 2, 3]
    async with weave() as w:

        @w.do(items)
        async def square_async(item):
            await asyncio.sleep(0.01)
            return item * item

        @w.do
        async def sum_squares_async(square_async):
            await asyncio.sleep(0.01)
            return sum(square_async)

    assert w.result["sum_squares_async"] == 14
    assert w.result["square_async"] == [1, 4, 9]


@pytest.mark.asyncio
async def test_error_in_map_cancels_others():
    """Tests that an exception in one mapped sub-task cancels others."""
    items = ["ok_long", "fail", "ok"]

    long_task_started = asyncio.Event()
    long_task_cancelled = False
    with pytest.raises(ValueError, match="Task failed on item: fail"):
        async with weave() as w:

            @w.do(items)
            async def process_item_with_failure(item):
                nonlocal long_task_cancelled
                if item == "ok":
                    await asyncio.sleep(0.1)  # should get cancelled
                    return "ok"
                elif item == "fail":
                    await long_task_started.wait()  # Make sure the long one starts
                    raise ValueError("Task failed on item: fail")
                elif item == "ok_long":
                    long_task_started.set()
                    try:
                        await asyncio.sleep(0.2)  # Long enough to be cancelled
                    except asyncio.CancelledError:
                        long_task_cancelled = True
                        raise
                    return "long_ok"

    assert long_task_cancelled, "The long-running sub-task should have been cancelled."
