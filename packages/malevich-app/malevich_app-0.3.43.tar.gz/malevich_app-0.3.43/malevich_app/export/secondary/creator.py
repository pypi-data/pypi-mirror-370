import importlib
import io
import json
import os
import threading
from copy import deepcopy
from typing import List, Optional, Any, Tuple, Dict, Union
from malevich_app.export.abstract.abstract import Cfg, App
from malevich_app.export.jls.JuliusApp import JuliusApp
from malevich_app.export.jls.jls import Wrapper
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.const import TEMP_FILES
from malevich_app.export.secondary.jls_imported import set_imported, set_imported2, set_imported3, set_imported4

__modules = []
__lock = threading.Lock()
__dummy_schemes_module = importlib.import_module("malevich_app.docker_export.schemes")
__dummy_schemes_module2 = importlib.import_module("malevich_app.export.secondary.creator")


def create_temp_dir():
    os.system(f"rm -rf {TEMP_FILES}")
    os.makedirs(TEMP_FILES)


def create_dummy_schemes(schemes_names: List[str]):     # TODO check exists for operation_id
    for schemes_name in schemes_names:
        update_dummy_scheme(schemes_name)


def update_dummy_scheme(scheme_name: str):
    if not hasattr(__dummy_schemes_module, scheme_name):
        setattr(__dummy_schemes_module, scheme_name, type(scheme_name, (), {"__dummy_scheme": None}))
    if not hasattr(__dummy_schemes_module2, scheme_name):   # FIXME
        setattr(__dummy_schemes_module2, scheme_name, type(scheme_name, (), {"__dummy_scheme": None}))


def do_cfg(text: Optional[str], info_url: str, is_run: bool = False, extension_key: str = "", *, all_extension_keys: bool = False) -> Tuple[Cfg, Optional[Union[Dict[str, str], str]]]:
    try:
        if text is None or text == "":
            assert not is_run, "cfg not set"
            json_cfg = {}
        else:
            json_cfg = json.loads(text)
    except BaseException as ex:
        raise EntityException(f"load cfg: {ex}")
    collections = json_cfg.get("collections") or {}
    different = json_cfg.get("different") or {}
    schemes_aliases = json_cfg.get("schemes_aliases") or {}
    msg_url = json_cfg.get("msg_url")
    init_apps_update = json_cfg.get("init_apps_update") or {}
    app_settings = json_cfg.get("app_settings") or []
    app_cfg_extension = json_cfg.get("app_cfg_extension") or {}
    if not all_extension_keys:
        app_cfg_extension = app_cfg_extension.get(extension_key, None)
    email = json_cfg.get("email")
    if msg_url is None:
        if info_url is not None:
            msg_url = info_url
    return Cfg(collections=collections, different=different, schemes_aliases=schemes_aliases, msg_url=msg_url, init_apps_update=init_apps_update, app_settings=app_settings, email=email), app_cfg_extension


def get_julius_app(app: Optional[App] = None, cfg: Optional[Cfg] = None, mode: str = "run", base_j_app: Optional[Any] = None, app_cfg_extension: Optional[str] = None, *args, **kwargs):
    assert mode == "run" or mode == "info" or mode == "init", "wrong julius app mode"
    with __lock:
        if mode == "run":   # FIXME
            assert base_j_app is not None, "internal error: init japp"
            Wrapper.app = base_j_app
        else:
            Wrapper.app = JuliusApp()
        Wrapper.app.logs_buffer = io.StringIO()

        set_imported(False)
        set_imported2(False)
        set_imported3(False)
        set_imported4(False)
        if app is not None:
            Wrapper.app.prepare(app.inputId, app.processorId, app.outputId)

        Wrapper.app.set_app_mode(mode)
        if mode == "info" or mode == "init":
            Wrapper.app._init(*args, **kwargs)
        if cfg is not None:
            Wrapper.app.set_cfg(cfg)
        if mode != "init" and app_cfg_extension is not None:
            try:
                extra_cfg = json.loads(app_cfg_extension)
                Wrapper.app.app_cfg.update(extra_cfg)
            except BaseException as ex:
                Wrapper.app.logs_buffer.write(f"extra app config load fail: {ex}\n")

        # schemes_module = importlib.import_module("malevich_app.docker_export.schemes")
        malevich_module = importlib.import_module("malevich")
        malevich_square_module = importlib.import_module("malevich.square")
        if not __modules:
            assert os.path.isdir("apps"), "apps directory should exist"
            for path, _, names in os.walk("apps"):
                for name in names:
                    if name[-3:] == ".py":
                        imported = set()
                        reimport = True
                        module_name = f"{path.replace('/', '.')}.{name[:-3]}"
                        while reimport:
                            try:
                                module = importlib.import_module(module_name)
                                importlib.reload(module)
                                __modules.append(module)
                                reimport = False
                            except ImportError as er:
                                if ("malevich" in er.name or "square" in er.name) and er.msg.startswith("cannot import name '"):
                                    msg = er.msg.replace("cannot import name '", "")
                                    scheme_name = msg[:msg.find("'")]
                                    if scheme_name in imported:
                                        Wrapper.app.logs_buffer.write(f"error: scheme \"{scheme_name}\" not found, reimport fail\n")
                                        reimport = False
                                    else:
                                        Wrapper.app.logs_buffer.write(f"warning: scheme \"{scheme_name}\" not found\n")
                                        imported.add(scheme_name)
                                        update_dummy_scheme(scheme_name)
                                        # importlib.reload(schemes_module)
                                        importlib.reload(malevich_module)
                                        importlib.reload(malevich_square_module)
                                else:
                                    raise er
        else:
            for module in __modules:
                importlib.reload(module)
        if mode == "init":
            Wrapper.app._validation()
            Wrapper.app._set_argnames()
        if mode == "run":
            Wrapper.app._set_collections_v1()
            common, Wrapper.app._context.common = Wrapper.app._context.common, None
        j_app = deepcopy(Wrapper.app)
        if mode == "run":
            Wrapper.app._context.common, j_app._context.common = common, common
        return j_app
