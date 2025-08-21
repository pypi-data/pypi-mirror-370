import asyncio
import threading

from malevich_app.export.processes.BoolWrapper import BoolWrapper
from malevich_app.export.secondary.LogHelper import log_error
from malevich_app.export.secondary.const import LOGS_STREAM_DELAY_S

__delay = LOGS_STREAM_DELAY_S
__dones = []
__lock = threading.Lock()
__lock_dones = threading.Lock()


async def background_single_task(finish: BoolWrapper, done: BoolWrapper, fun: callable, *args, **kwargs):
    global __dones, __lock, __lock_dones
    with __lock_dones:
        __dones.append(done)
    while not finish:
        __lock.acquire()
        if finish:
            __lock.release()
            break
        with __lock_dones:
            dones = __dones
            __dones = []
        try:
            await fun(*args, **kwargs)
        except BaseException as ex:
            log_error(f"background_single_task: {ex}")
        for done_i in dones:
            done_i.set(True)
        __lock.release()
        await asyncio.sleep(__delay)
