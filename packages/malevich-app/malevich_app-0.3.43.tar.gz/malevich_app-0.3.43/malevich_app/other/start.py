import os
import uvicorn
import asyncio

import malevich_app.export.secondary.const as C
from malevich_app.export.processes.main import logs_streaming_restart
from malevich_app.export.secondary.logger import logfile


if __name__ == "__main__":
    C.IS_LOCAL = False
    if C.IS_EXTERNAL:
        os.makedirs(C.MOUNT_PATH, exist_ok=True)
        os.makedirs(C.MOUNT_PATH_OBJ, exist_ok=True)
    if C.LOGS_STREAMING:
        asyncio.run(logs_streaming_restart(wait=False))
    else:
        open(logfile, 'a').close()
    uvicorn.run("malevich_app.export.api.api:app", host="0.0.0.0", port=int(os.environ["PORT"]), loop="asyncio", reload=False, workers=1)
