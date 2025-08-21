import logging
import sys
from typing import Optional
import malevich_app.export.secondary.const as C

_base_stdout = sys.stdout


def base_logger_fun(operation_id: str, run_id: Optional[str] = None, bind_id: Optional[str] = None, user_logs: bool = False) -> logging.Logger:
    logger = logging.getLogger(f"{operation_id}${run_id}${bind_id}${user_logs}")
    logger.setLevel(logging.INFO)
    logger.handlers = []

    handler = logging.StreamHandler(_base_stdout)
    if bind_id is None:
        logformat = f'%(asctime)s.%(msecs)03dZ: %(message)s'
    else:
        if user_logs:
            logformat = f'%(asctime)s.%(msecs)03dZ, {bind_id} (user): %(message)s'
        else:
            logformat = f'%(asctime)s.%(msecs)03dZ, {bind_id}: %(message)s'
    formatter = logging.Formatter(fmt=logformat, datefmt=C.TIME_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
