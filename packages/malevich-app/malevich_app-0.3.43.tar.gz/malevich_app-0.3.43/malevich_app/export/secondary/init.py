import io
import json
import os
import traceback
from typing import Optional, Tuple, List
import pandas as pd
import nest_asyncio
from malevich_app.export.abstract.abstract import App, AppFunctionsInfo, Cfg, AnyInit
from malevich_app.export.jls.helpers import run_func_in_threadpool
from malevich_app.export.secondary.LogHelper import log_error
from malevich_app.export.secondary.State import states
from malevich_app.export.secondary.const import TEMP_OBJ_DIR
from malevich_app.export.secondary.creator import get_julius_app, create_dummy_schemes, do_cfg, create_temp_dir, update_dummy_scheme


async def do_app(app: App, cfg: Cfg, mode: str, *args, **kwargs):
    j_app = await run_func_in_threadpool(get_julius_app, app=app, cfg=cfg, mode=mode, *args, **kwargs)
    assert j_app.input_fun_exists() or app.inputId is None, f"input fun with id = {app.inputId} not exist"
    assert j_app.processor_fun_exists(), f"processor fun with id = {app.processorId} not exist"
    assert j_app.output_fun_exists() or app.outputId is None, f"output fun with id = {app.outputId} not exist"
    return j_app


def get_app_cfg(cfg: Optional[str], buffer: io.StringIO):
    if cfg is None:
        return {}
    try:
        return json.loads(cfg)
    except BaseException as ex:
        buffer.write(f"incorrect cfg: {ex}\n")
        log_error(f"incorrect cfg: {ex}")


async def init_fun(init: AnyInit, mode="run", app_id=None, task_id=None, base_j_app=None, *args, **kwargs):
    state = states[init.operationId]
    if app_id is None:
        extension_key = f"${base_j_app.app_id}" if base_j_app.task_id is None else f"{base_j_app.task_id}${base_j_app.app_id}"
    else:
        extension_key = f"${app_id}" if task_id is None else f"{task_id}${app_id}"
    cfg, app_cfg_extension = do_cfg(init.cfg, init.infoUrl, mode == "run", extension_key=extension_key)
    if mode == "init":
        create_temp_dir()
        state.schemes_names.update(cfg.schemes_aliases.keys())
        create_dummy_schemes(state.schemes_names)
    else:   # run
        for scheme_name in cfg.schemes_aliases.keys():
            if scheme_name not in state.schemes_names:
                state.schemes_names.add(scheme_name)
                update_dummy_scheme(scheme_name)
    j_app = await do_app(state.app, cfg, mode, *args, app_cfg_extension=app_cfg_extension, app_id=app_id, task_id=task_id, base_j_app=base_j_app, **kwargs)
    j_app.set_exist_schemes(state.schemes_names)
    if mode == "init" and state.app.cfg is not None:
        j_app.app_cfg = get_app_cfg(state.app.cfg, j_app.logs_buffer)
    return j_app


async def info_fun(schemes_names: List[str], app_cfg: Optional[str] = None, *args, **kwargs) -> Tuple[AppFunctionsInfo, bool]:
    create_dummy_schemes(schemes_names)
    try:
        j_app = await run_func_in_threadpool(get_julius_app, mode="info", *args, **kwargs)
    except:
        return AppFunctionsInfo(logs=traceback.format_exc()), False
    if app_cfg is not None:
        j_app.app_cfg = get_app_cfg(app_cfg, j_app.logs_buffer)
    return j_app.info(), True


def init_settings_main():
    os.makedirs(TEMP_OBJ_DIR, exist_ok=True)
    pd.set_option('display.max_columns', None)
    nest_asyncio.apply()
