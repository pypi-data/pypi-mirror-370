import asyncio
import time

import pytest

from pyxxl.ctx import g
from pyxxl.executor import HandlerInfo


@pytest.mark.asyncio
async def test_async_timeout():
    r = []

    async def _handler():
        while True:
            await asyncio.sleep(0.5)
            r.append(1)

    handler = HandlerInfo(handler=_handler)
    with pytest.raises(asyncio.TimeoutError):
        await handler.start(2)

    await asyncio.sleep(1)
    now_r_num = len(r)
    await asyncio.sleep(2)
    assert len(r) == now_r_num


@pytest.mark.asyncio
async def test_sync_timeout_ok(event_loop):
    r = []

    def _handler():
        while len(r) < 10 and not g.cancel_event.is_set():
            time.sleep(0.5)
            r.append(1)

    handler = HandlerInfo(handler=_handler)
    with pytest.raises(asyncio.TimeoutError):
        await handler.start(2)

    await asyncio.sleep(1)
    now_r_num = len(r)
    await asyncio.sleep(2)
    assert len(r) == now_r_num


@pytest.mark.asyncio
async def test_sync_timeout_error(event_loop):
    r = []

    def _handler():
        while len(r) < 10:  # 防止测试线程卡死
            time.sleep(0.5)
            r.append(1)

    handler = HandlerInfo(handler=_handler)
    with pytest.raises(asyncio.TimeoutError):
        await handler.start(2)

    await asyncio.sleep(1)
    now_r_num = len(r)
    await asyncio.sleep(2)
    assert len(r) > now_r_num
