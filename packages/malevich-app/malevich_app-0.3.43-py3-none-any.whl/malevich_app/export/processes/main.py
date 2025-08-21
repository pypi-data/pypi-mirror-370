import asyncio

from malevich_app.export.processes.BoolWrapper import BoolWrapper
from malevich_app.export.processes.utils import background_single_task
from malevich_app.export.secondary.const import SLEEP_BACKGROUND_TASK_S, WAIT_DELAY_S
from malevich_app.export.secondary.helpers import send_background_task
from malevich_app.export.secondary.logsStreaming import logs_streaming_iteration

__logs_streaming_finish = None


async def logs_streaming_restart(wait: bool = True):
    global __logs_streaming_finish
    if __logs_streaming_finish is not None:
        __logs_streaming_finish.set(True)
    __logs_streaming_finish = BoolWrapper()
    done = BoolWrapper()
    send_background_task(background_single_task, __logs_streaming_finish, done, logs_streaming_iteration)
    await asyncio.sleep(SLEEP_BACKGROUND_TASK_S)
    if not wait:
        return
    while not done:
        await asyncio.sleep(WAIT_DELAY_S)
