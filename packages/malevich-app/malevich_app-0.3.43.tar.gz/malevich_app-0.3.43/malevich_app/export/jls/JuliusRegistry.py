import importlib
import io
import json
import logging
import os
from copy import deepcopy
from functools import cached_property
from typing import Dict, Any, Optional, Tuple, List, Callable, Set
import pandas as pd
from asyncio import gather
from mypy_extensions import VarArg
from pydantic import BaseModel
from malevich_app.export.abstract.abstract import PipelineApp, Cfg, AppFunctionsInfo, InputFunctionInfo, \
    ProcessorFunctionInfo, \
    OutputFunctionInfo, ConditionFunctionInfo, InitInfo, AnyInit, TempRunScheme, FunctionInfo
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.JuliusApp import JuliusApp
from malevich_app.export.jls.LocalLogsBuffer import LocalLogsBuffer
from malevich_app.export.jls.df import get_fun_info_verbose, get_context_argname, JDF, get_fun_info, get_context_info
from malevich_app.export.jls.jls import Wrapper
from malevich_app.export.kafka.KafkaHelper import KafkaHelper
from malevich_app.export.request.core_requests import post_request_json
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.LocalDfs import LocalDfs
from malevich_app.export.secondary.ProfileMode import ProfileMode
from malevich_app.export.secondary.creator import update_dummy_scheme
import malevich_app.export.secondary.const as C
import malevich_app.export.secondary.endpoints as end
from malevich_app.export.secondary.helpers import json_schema

_registered = False


class JuliusEmptyRegistry:
    def __init__(self):
        pass

    def create_app(self, init: AnyInit, bind_id: str, cfg: Cfg, pipeline_app: Optional[PipelineApp] = None, app_cfg_extension: Optional[str] = None) -> JuliusApp:
        raise Exception("create app i empty registry")

    def register_input(self, fun: callable, id: Optional[str], *args, **kwargs):
        pass

    def register_processor(self, fun: callable, id: Optional[str], *args, **kwargs):
        pass

    def register_output(self, fun: callable, id: Optional[str], *args, **kwargs):
        pass

    def register_condition(self, fun: callable, id: Optional[str], *args, **kwargs):
        pass

    def register_scheme(self, cl: BaseModel):
        pass

    def register_init(self, fun: callable, id: Optional[str], *args, **kwargs):
        pass


class JuliusRegistry(JuliusEmptyRegistry):
    def __init__(self, import_dirs: Optional[List[str]] = None, logger_fun: Optional[Callable[[str, Optional[str], Optional[str], bool], logging.Logger]] = None, with_import_restrictions: bool = True):
        super().__init__()
        Wrapper.app = self

        self.__is_local = False
        self.__import_dirs = import_dirs or [C.APPS_DIR]
        self.__import_restrictions = [f"{dir.removeprefix(os.sep).removesuffix(os.sep).replace(os.sep, '.')}." for dir in self.__import_dirs] if with_import_restrictions else None
        self.__logger_fun = logger_fun
        self.__local_storage: Optional['LocalStorage'] = None
        self.logs_buffer = io.StringIO()
        self.__inputs: Dict[str, Any] = {}      # only for get info
        self.__processors: Dict[str, Any] = {}
        self.__outputs: Dict[str, Any] = {}
        self.__conditions: Dict[str, Any] = {}
        self.__schemes: Dict[str, Any] = {}
        self.__inits: Dict[str, Any] = {}

        self.__schemes_info_processors: Dict[str, Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]] = {}
        self.__schemes_info_outputs: Dict[str, Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]] = {}
        self.__schemes_info_conditions: Dict[str, Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]] = {}
        self.__base_j_apps: Dict[str, Dict[str, JuliusApp]] = {}        # operation_id -> bind_id -> base_j_app

        self.__exist_schemes = set()
        self.__register()
        Wrapper.app = JuliusEmptyRegistry()

    def _set_local_storage(self, local_storage: 'LocalStorage'):
        assert not self.__is_local, "double set local_storage in registry"
        self.__local_storage = local_storage
        self.__is_local = True

    def __register(self):
        lib_modules = [importlib.import_module("malevich"), importlib.import_module("malevich.square"), importlib.import_module("malevich_app.square")] # TODO import "defaults"

        for dir in self.__import_dirs:
            assert os.path.isdir(dir), f"{dir} directory should exist"
        imported = set()

        global _registered
        for import_dir in self.__import_dirs:
            for path, dirs, names in os.walk(import_dir):
                dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("__")]
                for name in names:
                    if name[-3:] == ".py":
                        reimport = True
                        failed = False
                        module_name = f"{path.removeprefix('.').removeprefix(os.sep).replace(os.sep, '.')}.{name[:-3]}"
                        if _registered:
                            failed = True  # force reload
                        while reimport:
                            try:
                                module = importlib.import_module(module_name)
                                if failed:
                                    importlib.reload(module)
                                reimport = False
                            except ImportError as er:
                                if er.msg.startswith("cannot import name '") and ("malevich" in er.name or "square" in er.name) and not C.REGISTER_RAISE_ON_ERROR:
                                    failed = True
                                    msg = er.msg.replace("cannot import name '", "")
                                    scheme_name = msg[:msg.find("'")]
                                    if scheme_name in imported:
                                        self.logs_buffer.write(f"error: scheme \"{scheme_name}\" not found, reimport fail\n")
                                        reimport = False
                                    else:
                                        # self.logs_buffer.write(f"warning: scheme \"{scheme_name}\" not found\n")
                                        imported.add(scheme_name)
                                        update_dummy_scheme(scheme_name)
                                        for lib_module in lib_modules:  # TODO ?
                                            importlib.reload(lib_module)
                                else:
                                    raise er
        _registered = True

    def __function_info_with_tags(self, fun_info: FunctionInfo, tags: Optional[Dict[str, str]]) -> FunctionInfo:
        if tags is None:
            return fun_info
        try:
            fun_info.tags = tags
            fun_info.model_validate(fun_info.model_dump(), strict=True)
        except:
            fun_info.tags = None
        return fun_info

    @cached_property
    def info(self) -> AppFunctionsInfo:
        return AppFunctionsInfo(
            inputs={id: self.__function_info_with_tags(InputFunctionInfo(id=id, name=args[0].__name__, arguments=get_fun_info_verbose(args[0]), doc=args[0].__doc__, finishMsg=kwargs["finish_msg"], mode=kwargs["mode"].value, cpuBound=kwargs["cpu_bound"]), tags=kwargs["tags"]) for id, (args, kwargs) in self.__inputs.items()},
            processors={id: self.__function_info_with_tags(ProcessorFunctionInfo(id=id, name=args[0].__name__, arguments=get_fun_info_verbose(args[0]), doc=args[0].__doc__, finishMsg=kwargs["finish_msg"], contextClass=get_context_info(get_fun_info(args[0])[0]), cpuBound=kwargs["cpu_bound"], isStream=kwargs["is_stream"]), tags=kwargs["tags"]) for id, (args, kwargs) in self.__processors.items()},     # TODO contextClass
            outputs={id: self.__function_info_with_tags(OutputFunctionInfo(id=id, name=args[0].__name__, arguments=get_fun_info_verbose(args[0]), doc=args[0].__doc__, finishMsg=kwargs["finish_msg"], collectionOutNames=kwargs["collection_out_names"] if (collection_out_name := kwargs["collection_out_name"]) is None else [collection_out_name], cpuBound=kwargs["cpu_bound"]), tags=kwargs["tags"]) for id, (args, kwargs) in self.__outputs.items()},
            conditions={id: self.__function_info_with_tags(ConditionFunctionInfo(id=id, name=args[0].__name__, arguments=get_fun_info_verbose(args[0]), doc=args[0].__doc__, finishMsg=kwargs["finish_msg"], cpuBound=kwargs["cpu_bound"]), tags=kwargs["tags"]) for id, (args, kwargs) in self.__conditions.items()},
            schemes={id: json_schema(cl) for id, cl in self.__schemes.items()},
            inits={id: self.__function_info_with_tags(InitInfo(id=id, enable=kwargs["enable"], tl=kwargs["tl"], prepare=kwargs["prepare"], argname=get_context_argname(args[0]), doc=args[0].__doc__, cpuBound=kwargs["cpu_bound"]), tags=kwargs["tags"]) for id, (args, kwargs) in self.__inits.items()},
            logs=self.logs_buffer.getvalue(),
        )

    def schemes(self) -> Dict[str, Any]:
        return self.__schemes

    async def save_schemes(self, operation_id: str):
        path = C.SCHEMES_PATH(operation_id)
        os.makedirs(path, exist_ok=True)

        for id, cl in self.__schemes.items():
            with open(os.path.join(path, id), 'w') as f:
                f.write(json_schema(cl))

        if C.WS is not None:
            await self.update_schemes_pipeline(operation_id, prefix=False)

    async def update_schemes_pipeline(self, operation_id: str, prefix: bool = True):
        tasks = []
        for name, cl in self.__schemes.items():
            data = json_schema(cl)
            temp_run_scheme = TempRunScheme(operationId=operation_id, data=data, name=name, prefix=prefix)
            if not self.__is_local or C.WS is not None:
                tasks.append(post_request_json(end.RUN_SCHEME, temp_run_scheme.model_dump_json(), text=True, buffer=self.logs_buffer))
        if len(tasks) > 0:
            await gather(*tasks)

    @property
    def internal_schemes(self) -> Set[str]:
        return set(self.__schemes.keys())

    def get_schemes_info(self, id: str, operation: EntityType) -> Optional[Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]]:
        if operation == EntityType.PROCESSOR:
            res = self.__schemes_info_processors.get(id)
        elif operation == EntityType.OUTPUT:
            res = self.__schemes_info_outputs.get(id)
        elif operation == EntityType.CONDITION:
            res = self.__schemes_info_conditions.get(id)
        else:
            raise Exception("wrong operation, update scheme info")
        if res is None:
            raise Exception(f"{operation.value} with id={id} not found")
        return res

    def create_app(self, init: AnyInit, bind_id: str, cfg: Optional[Cfg], pipeline_app: Optional[PipelineApp] = None, app_cfg: Any = None, app_cfg_extension: Optional[str] = None, local_dfs: Optional[LocalDfs] = None, *args, **kwargs) -> JuliusApp:
        operation_id = init.operationId
        is_init = pipeline_app is not None

        if is_init:
            if self.__logger_fun is None:
                logs_buffer = io.StringIO()
            else:
                logs_buffer = LocalLogsBuffer(self.__logger_fun, operation_id, None, bind_id)
            assert app_cfg_extension is None, "override cfg should be None in init"
            local_storage = self.__local_storage if C.WS is None else None
            j_app = JuliusApp(version=2, local_dfs=local_dfs, exist_schemes=self.__exist_schemes, local_storage=local_storage, logger_fun=self.__logger_fun)
            op_base_j_apps = self.__base_j_apps.get(operation_id)
            if op_base_j_apps is None:
                op_base_j_apps = {}
                self.__base_j_apps[operation_id] = op_base_j_apps
            op_base_j_apps[bind_id] = j_app

            j_app.prepare(proc_id=pipeline_app.processorId, out_id=pipeline_app.outputId, cond_id=pipeline_app.conditionId)
            j_app.set_app_mode("init")
            j_app._init(operation_id, bind_id, *args, **kwargs)

            j_app.debug_mode = init.debugMode
            j_app.dag_host_port = C.DAG_HOST_PORT(init.dagHost)
            j_app.run_id = "prepare"
            j_app.profile_mode = ProfileMode.from_str(init.profileMode)
            j_app.secret = init.secret
            j_app._single_pod = init.singlePod
            j_app._login = init.login
            if cfg is not None:
                j_app.set_cfg(cfg)
            j_app.logs_buffer = logs_buffer
            j_app.app_cfg = app_cfg
        else:
            j_app = self.__base_j_apps.get(operation_id, {}).get(bind_id)
            if self.__logger_fun is not None:
                j_app.logs_buffer.update_run_id(init.runId)
            if app_cfg_extension is not None:  # TODO fix it if not copy later
                try:
                    app_cfg_extension = json.loads(app_cfg_extension)
                except BaseException as ex:
                    j_app.logs_buffer.write(f"extra app config load fail: {ex}\n")
                    app_cfg_extension = {}

            assert j_app is not None, f"base julius app for operation_id={operation_id} and bind_id={bind_id} not exist"
            j_app.set_app_mode("run")

            j_app.debug_mode = init.debugMode
            j_app.dag_host_port = C.DAG_HOST_PORT(init.dagHost)
            j_app.run_id = init.runId
            j_app.profile_mode = ProfileMode.from_str(init.profileMode)
            j_app._operation_id = operation_id
            if init.kafkaInitRun is not None:
                j_app.kafka_helper = KafkaHelper(init.kafkaInitRun, j_app)
            if cfg is not None:
                j_app.set_cfg(cfg)
            else:
                assert j_app.exist_cfg(), "config should set"
            j_app.set_context()

        if is_init:
            if pipeline_app.processorId is not None:
                args_kwargs = self.__processors.get(pipeline_app.processorId)
                if args_kwargs is None:
                    raise EntityException(f"processor {pipeline_app.processorId} not exist")
                args, kwargs = args_kwargs
                j_app.register_processor(*args, **kwargs)
            if pipeline_app.outputId is not None:
                args_kwargs = self.__outputs.get(pipeline_app.outputId)
                if args_kwargs is None:
                    raise EntityException(f"output {pipeline_app.outputId} not exist")
                args, kwargs = args_kwargs
                j_app.register_output(*args, **kwargs)
            if pipeline_app.conditionId is not None:
                args_kwargs = self.__conditions.get(pipeline_app.conditionId)
                if args_kwargs is None:
                    raise EntityException(f"condition {pipeline_app.conditionId} not exist")
                args, kwargs = args_kwargs
                j_app.register_condition(*args, **kwargs)
            for name, scheme in self.__schemes.items():
                j_app.register_scheme(scheme, name=name)
            for init_args_kwargs in self.__inits.values():
                args, kwargs = init_args_kwargs
                j_app.register_init(*args, **kwargs)
            j_app.set_context()
            return j_app

        common, j_app._context.common = j_app._context.common, None
        local_dfs_temp, j_app.local_dfs = j_app.local_dfs, None
        copy_j_app = deepcopy(j_app)
        if app_cfg_extension is not None:
            copy_j_app.app_cfg.update(app_cfg_extension)    # TODO check updated context.app_cfg
        copy_j_app._context.common, j_app._context.common = common, common
        copy_j_app.local_dfs, j_app.local_dfs = local_dfs_temp, local_dfs_temp
        return copy_j_app

    def delete_app(self, operation_id: str, bind_id: str):  # TODO use it
        j_apps = self.__base_j_apps.get(operation_id)
        if j_apps is not None:
            if len(j_apps) == 1:
                self.__base_j_apps.pop(operation_id)
            else:
                j_apps.pop(bind_id)

    def __register_entity(self, ent) -> bool:
        if self.__import_restrictions is None:
            return True

        module = ent.__module__
        for m in self.__import_restrictions:
            if m in module:
                return True
        return False

    def register_input(self, fun: callable, id: Optional[str], *args, **kwargs):
        if not self.__register_entity(fun):
            return
        if id is None:
            id = fun.__name__
        self.__inputs[id] = ((fun, id, *args), kwargs)

    def register_processor(self, fun: callable, id: Optional[str], *args, **kwargs):
        if not self.__register_entity(fun):
            return
        if id is None:
            id = fun.__name__
        self.__processors[id] = ((fun, id, *args), kwargs)
        self.__schemes_info_processors[id] = get_fun_info(fun, by_names=True)

    def register_output(self, fun: callable, id: Optional[str], *args, **kwargs):
        if not self.__register_entity(fun):
            return
        if id is None:
            id = fun.__name__
        self.__outputs[id] = ((fun, id, *args), kwargs)
        self.__schemes_info_outputs[id] = get_fun_info(fun, by_names=True)

    def register_condition(self, fun: callable, id: Optional[str], *args, **kwargs):
        if not self.__register_entity(fun):
            return
        if id is None:
            id = fun.__name__
        self.__conditions[id] = ((fun, id, *args), kwargs)
        self.__schemes_info_conditions[id] = get_fun_info(fun, by_names=True)

    def register_scheme(self, cl: BaseModel):
        if not self.__register_entity(cl):
            return
        id = cl.__name__
        self.__schemes[id] = cl

    def register_init(self, fun: callable, id: Optional[str], *args, **kwargs):
        if not self.__register_entity(fun):
            return
        if id is None:
            id = fun.__name__
        self.__inits[id] = ((fun, id, *args), kwargs)
