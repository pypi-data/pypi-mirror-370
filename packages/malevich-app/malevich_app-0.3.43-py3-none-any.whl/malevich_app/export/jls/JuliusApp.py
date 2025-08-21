import asyncio
import io
import logging
import numpy
import pandas as pd
from asyncio import gather
from copy import copy
from typing import List, Optional, Tuple, Any, Dict, Set, Callable, Union
from mypy_extensions import VarArg
from pydantic import BaseModel
import malevich_app.export.secondary.const as C
import malevich_app.export.secondary.endpoints as end
from malevich_app.docker_export.funcs import docker_mode
from malevich_app.docker_export.helpers import LocalDfsSpark
from malevich_app.export.abstract.abstract import QueryCollection, Credentials, CollectionOutside, DBQuery, TempRunScheme, \
    InputFunctionInfo, AppFunctionsInfo, ProcessorFunctionInfo, OutputFunctionInfo, Cfg, InitInfo, ConditionFunctionInfo
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import get_fun_info, JDF, get_fun_info_verbose, get_context_argname, get_argnames, get_context_info, \
    get_model_name, get_annotations, get_argcount
from malevich_app.export.kafka.KafkaHelper import KafkaHelper
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.InitFunState import InitFunState, InitFunError
from malevich_app.export.secondary.LocalDfs import LocalDfs
from malevich_app.export.secondary.LogHelper import log_warn, log_error
from malevich_app.export.secondary.ProfileMode import ProfileMode
from malevich_app.export.secondary.State import states, State
from malevich_app.export.jls.WrapperMode import InputWrapper
from malevich_app.export.jls.helpers import get_params_names, run_func, Object, PreContext
from malevich_app.export.request.core_requests import post_request_json, post_error_info
from malevich_app.export.request.download import download_google_drive
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.FileCollection import FileCollection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.collection.MongoCollection import MongoCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.const import TEMP_FILES, CONTEXT, FINISH_SUBJ, DOC_SCHEME_PREFIX, CONTEXT_TYPE, DOCS_SCHEME_PREFIX
from malevich_app.export.secondary.fail_storage import fail_structure
from malevich_app.export.secondary.helpers import get_db_type_by_url, ContextPosition, json_schema
from malevich_app.export.secondary.redirect import redirect_out
from malevich_app.export.secondary.trace import format_exc_skip
from malevich_app.jls_lib.utils import Context, MalevichException

_default_schemes = {"default_scheme", "obj", "OBJ", "", None}


class JuliusApp:
    def __init__(self, version=0, *, local_dfs: Optional[LocalDfs] = None, exist_schemes: Optional[Set[str]] = None, local_storage: Optional['LocalStorage'] = None, logger_fun: Optional[Callable[[str, Optional[str], Optional[str], bool], logging.Logger]] = None):
        assert docker_mode in ["python", "dask", "pyspark"]
        self.__mode = None
        self.__info = AppFunctionsInfo()
        self.__operation: EntityType = None
        self.__input_fun = None
        self.__processor_fun = None
        self.__output_fun = None
        self.__condition_fun = None
        self.__input_cpu_bound = False
        self.__processor_cpu_bound = False
        self.__output_cpu_bound = False
        self.__condition_cpu_bound = False
        self.__processor_is_stream = False
        self.__input_finish_msg = None
        self.__processor_finish_msg = None
        self.__output_finish_msg = None
        self.__condition_finish_msg = None
        self.__processor_drop_internal = None
        self.__processor_get_scale_part_all = None
        self.__output_drop_internal = None
        self.__condition_drop_internal = None
        self.__schemes_info_input: Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]] = None
        self.__schemes_info_processor: Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]] = None
        self.__schemes_info_output: Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]] = None
        self.__schemes_info_condition: Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]] = None
        self.__schemes = dict()     # defined with jls.scheme
        self.__schemes_send = set()
        self._input_id = None
        self._processor_id = None
        self._output_id = None
        self._condition_id = None
        self.__input_context_pos = ContextPosition.NONE
        self.__processor_context_pos = ContextPosition.NONE
        self.__output_context_pos = ContextPosition.NONE
        self.__condition_context_pos = ContextPosition.NONE
        self.__context_funcs: Dict[str, Any] = {}
        self.__fun_id_to_context_param: Dict[str, str] = {}
        self.__input_mode = None
        self.collections: List[Tuple[Collection, ...]] = []
        self.stream: Optional[callable] = None
        self.extra_collections: List[Tuple[Collection, ...]] = []
        self.sink_collections: List[Tuple[Collection, ...]] = []
        self.collection_out_names: Optional[List[str]] = None
        self.__input_collection_from = None
        self.__input_collections_from = None
        self.__input_extra_collection_from = None
        self.__input_extra_collections_from = None
        self.__input_df_by_args: bool = None
        self.__cfg: Cfg = None
        self._context: Context = PreContext()    # any value from _contexts
        self._contexts: Dict[str, Context] = {}
        self.__init_funs: List[InitFunState] = []
        self.__init_funs_first: List[InitFunState] = []
        self.__exist_schemes: Set[str] = exist_schemes if exist_schemes is not None else set()  # TODO improve work with them
        self.__is_local = local_storage is not None
        self._local_storage = local_storage
        self.__logger_fun = logger_fun
        self.docker_mode = docker_mode
        self.run_id: str = None
        self.debug_mode = False
        self.profile_mode: ProfileMode = None
        self.secret: str = None
        self._single_pod: bool = None
        self.dag_host_port: str = None
        self.continue_after_processor: bool = None
        self.__sink_names = None
        self.__cur_task = None

        self.app_cfg: Dict[str, Any] = dict()
        self.local_dfs: LocalDfs = local_dfs if local_dfs is not None else (LocalDfs() if self.docker_mode != "pyspark" else LocalDfsSpark())
        self.kafka_helper: KafkaHelper = None
        self.metadata: Dict[str, Optional[str]] = dict()
        self.save_collections_name: Optional[List[str]] = None     # extra save name from cfg

        # state
        self.__operation_id = None
        self._login = None
        self.app_id = None
        self.task_id = None
        self.__index: Optional[int] = None
        self.__scale: Optional[int] = None
        self.__override_extra_collections_names: Optional[Dict[str, List[str]]] = None
        self.__argnames: Dict[str, int] = {}        # dict argname -> index (without context) for processor
        self.__is_sink: bool = False
        self.__extra_argnames: Dict[str, int] = {}  # dict extra argname -> index (without context) for processor
        self.__app_version = version

        # logs for run_id
        self.logs_buffer: io.StringIO = None

    def _init(self, operation_id: str, app_id: str, task_id: Optional[str] = None, index: Optional[int] = None, scale: Optional[int] = None, extra_collections_from: Optional[Dict[str, List[str]]] = None):
        assert self.__operation_id is None, "japp already inited"
        self.__operation_id = operation_id
        self.app_id = app_id
        self.task_id = task_id
        self.__index = index
        self.__scale = scale
        if extra_collections_from is not None and self.__app_version == 0:
            self.__app_version = 1
            self.__override_extra_collections_names = {} if extra_collections_from is None else extra_collections_from

    def _set_collections_v1(self):
        if not self.input_fun_exists() and self.__app_version > 0:
            self.__set_collections()

    def _set_pauses(self, pauses: Dict[str, asyncio.Future]):
        for context in self._contexts.values():
            context._set_pauses(pauses)

    def _set_argnames(self):    # self.__override_extra_collections_names not valid after this
        if self.__app_version > 0:
            argnames = get_argnames(self.__processor_fun)   # TODO check is None

            sink_index = self.__schemes_info_processor[2]
            if sink_index is not None:
                sink_name = argnames[sink_index]
                new_names = self.__override_extra_collections_names.pop(sink_name, None)
                if new_names is not None:
                    self.__sink_names = new_names
                if self.start_processor_context_pos():
                    sink_index -= 1
                self.__argnames[sink_name] = sink_index
                self.__is_sink = True
            if self.start_processor_context_pos():
                argnames = argnames[1:]
            elif self.__processor_context_pos == ContextPosition.END:
                argnames = argnames[:-1]
            for i, name in enumerate(argnames):
                if i == sink_index:
                    continue

                new_names = self.__override_extra_collections_names.pop(name, None)
                if new_names is None:
                    new_name = None
                else:
                    if len(new_names) != 1:
                        raise EntityException(f"extra_collections_from not supported multiple collection names by argname {name}")
                    new_name = new_names[0]
                if new_name is not None:
                    self.__extra_argnames[new_name] = i
                else:
                    self.__argnames[name] = i

    def __set_collections(self):
        if self.kafka_helper is None and self.__mode == "run":
            if self.state.is_init_app:
                asyncio.run(self.__set_collections_from_cfg())
            asyncio.run(self.__set_extra_collections_from_cfg())

    @property
    def is_local(self) -> bool:
        return self.__is_local

    @property
    def operation_id(self) -> str:
        return self.__operation_id

    def set_index(self, index: int):
        for context in self._contexts.values():
            context._set_index(index)

    @property
    def get_scale_part_all(self) -> bool:
        return self.__processor_get_scale_part_all

    @property
    def state(self) -> State:
        return states[self.__operation_id]

    def set_cfg(self, cfg: Cfg):
        self.__cfg = cfg
        self.__set_save_collections_name()

    def get_cfg(self) -> Cfg:   # FIXME remove
        return self.__cfg

    def exist_cfg(self) -> bool:
        return self.__cfg is not None

    def __set_save_collections_name(self):
        for app_setting in self.__cfg.app_settings:
            if app_setting.taskId == self.task_id and app_setting.appId == self.app_id:
                if app_setting.saveCollectionsName is None:
                    pass
                elif isinstance(app_setting.saveCollectionsName, str):
                    self.save_collections_name = [app_setting.saveCollectionsName]
                else:
                    self.save_collections_name = app_setting.saveCollectionsName

    def set_context(self):
        common = self._context.common if not isinstance(self._context, PreContext) else Object()

        if len(self.__context_funcs) == 0:
            context = Context(self.__operation_id, self.run_id, self.app_id, self.app_cfg, self.__cfg.msg_url, self.__cfg.email, self.dag_host_port, self.secret, self._single_pod, self.__scale or self.state.scale, self.__index, self._login, self.logs_buffer, self._local_storage, self.__logger_fun)
            context.common = common
            self._contexts[None] = context
            self._context = context
        else:
            context = None
            for name, context_fun in self.__context_funcs.items():
                if context is None:
                    context = context_fun(self.__operation_id, self.run_id, self.app_id, self.app_cfg, self.__cfg.msg_url, self.__cfg.email, self.dag_host_port, self.secret, self._single_pod, self.__scale or self.state.scale, self.__index, self._login, self.logs_buffer, self._local_storage, self.__logger_fun)
                    context.common = common
                    context._fix_app_cfg()
                    self._contexts[name] = context
                    self._context = context
                else:
                    context_ = copy(context)
                    context_._fix_app_cfg(context_fun(initialize=False))
                    self._contexts[name] = context_

    def _get_context(self, fun_id):
        param_name = self.__fun_id_to_context_param.get(fun_id)
        return self._contexts[param_name]

    def set_exist_schemes(self, schemes: Set[str]):
        self.__exist_schemes.update(schemes)

    def set_for_kafka(self):
        if self.state.is_init_app:
            input_collections = self.get_input_collections()
            self.kafka_helper.set_collection_names(input_collections)
        extra_input_collections = self.get_extra_input_collections()
        if extra_input_collections is not None:
            self.kafka_helper.set_extra_collection_names(extra_input_collections)

    def update_metadata(self, collections_list: List[Tuple[Collection]]):
        context_pos = self.__get_context_pos()
        metadata = {}
        if context_pos != ContextPosition.NONE:
            func = None
            if self.__operation == EntityType.INPUT:
                func = self.__input_fun
            elif self.__operation == EntityType.PROCESSOR:
                func = self.__processor_fun
            elif self.__operation == EntityType.OUTPUT:
                func = self.__output_fun
            elif self.__operation == EntityType.CONDITION:
                func = self.__condition_fun
            else:
                log_warn("wrong update_metadata call")
            if func is not None:
                params_names = get_params_names(func)
                if self.__input_context_pos == ContextPosition.START:
                    params_names.pop(0)
                else:
                    params_names.pop()
                for param, collections in zip(params_names, collections_list):
                    metadata_list = []
                    for collection in collections:
                        if isinstance(collection, Collection):
                            metadata_list.append(self.metadata.get(collection.get()))
                        else:
                            metadata_list.append(None)
                            self.logs_buffer.write("error: wrong collections in julius_app.update_metadata\n")
                            log_warn("wrong collections in julius_app.update_metadata")
                    metadata[param] = metadata_list
        self._context._set_metadata(metadata)

    @property
    def input_df_by_args(self) -> bool:
        return self.__input_df_by_args

    def set_app_mode(self, mode: str):
        self.__mode = mode

    def info(self) -> AppFunctionsInfo:
        assert self.__mode == "info"
        self.__info.logs = self.logs_buffer.getvalue()
        self.logs_buffer.truncate(0)
        self.logs_buffer.seek(0)
        return self.__info

    @property
    def fun_arguments(self, with_ctx: bool = False) -> Tuple[str, ...]:
        if self.__processor_fun is not None:
            args = get_argnames(self.__processor_fun)
            if not with_ctx:
                if self.__processor_context_pos == ContextPosition.START:
                    args = args[1:]
                elif self.__processor_context_pos == ContextPosition.END:
                    args = args[:-1]
        else:
            args = get_argnames(self.__condition_fun)
            if not with_ctx:
                if self.__condition_context_pos == ContextPosition.START:
                    args = args[1:]
                elif self.__condition_context_pos == ContextPosition.END:
                    args = args[:-1]
        return args

    @property
    def fun_id(self) -> str:
        return self._processor_id or self._condition_id

    def get_input_mode(self):
        return self.__input_mode

    def get_scale_part(self, jdf: JDF) -> JDF:
        return self._context.get_scale_part(jdf)

    def get_input_collections(self, raises: bool = True) -> Optional[List[str]]:
        if self.__app_version > 0:
            if raises:
                if self.__is_sink:
                    if self.state.is_init_app and len(self.__argnames) != 1:
                        raise EntityException(f"not set extra_collections_from for {list(self.__argnames.keys())}")
                else:
                    if self.state.is_init_app and len(self.__argnames) != 0:
                        raise EntityException(f"not set extra_collections_from for {list(self.__argnames.keys())}")
            return []
        else:
            if raises:
                if self.__input_collections_from is not None and self.__input_collection_from is not None:
                    raise EntityException(f"only one way to set collections (app id={self.app_id})")
            elif self.__input_collections_from is not None and self.__input_collection_from is not None:
                self.logs_buffer.write(f"error: only one way to set collections (app id={self.app_id})\n")
                return []
            if self.__input_collections_from is None and self.__input_collection_from is None:
                return None
            return self.__input_collections_from if self.__input_collections_from is not None else [self.__input_collection_from]

    def get_extra_input_collections(self):
        if self.__app_version > 0:
            return list(self.__extra_argnames.keys())
        else:
            if self.__input_extra_collections_from is not None and self.__input_extra_collection_from is not None:
                raise EntityException(f"only one way to set extra collections (app id={self.app_id})")
            if self.__input_extra_collections_from is None and self.__input_extra_collection_from is None:
                return None
            return self.__input_extra_collections_from if self.__input_extra_collections_from is not None else [self.__input_extra_collection_from]

    def check_collection(self, collection: Collection, scheme: Union[Optional[str], Tuple[Optional[str]], List[Optional[str]]]):
        if isinstance(scheme, Tuple) or isinstance(scheme, List):
            for subscheme in scheme:
                self.__check_scheme(subscheme)
        else:
            self.__check_scheme(scheme)
        self.__check_collection(collection)

    def __check_scheme(self, scheme: Optional[str]):
        if scheme is not None:
            scheme = scheme.removeprefix(DOC_SCHEME_PREFIX).removeprefix(DOCS_SCHEME_PREFIX).removesuffix('*')
        if scheme not in _default_schemes and scheme not in self.__exist_schemes:
            self.__exist_schemes.add(scheme)  # to ignore this later
            self.logs_buffer.write(f"warn: scheme \"{scheme}\" not exist\n")

    def __check_collection(self, collection: Collection):
        if self.kafka_helper is not None:
            if not isinstance(collection, LocalCollection):
                raise EntityException("interpretation: collection not exist locally")

    async def __set_collections_from_cfg(self):
        collections_from = self.get_input_collections()
        collections_from = [] if collections_from is None else collections_from
        self.collections = []
        for collection_from in collections_from:
            if collection_from in self.__cfg.collections:
                self.collections.append((await self.__create_collection(collection_from),))
            else:
                self.logs_buffer.write(f"warning: not found collection with id={collection_from} in config (app id={self.app_id})\n")
                log_warn(f"warning: not found collection with id={collection_from} in config (app id={self.app_id})")
                self.collections.append(None)

    async def __set_extra_collections_from_cfg(self):
        extra_collections_from = self.get_extra_input_collections()
        extra_collections_from = [] if extra_collections_from is None else extra_collections_from
        self.extra_collections = []
        for extra_collection_from in extra_collections_from:
            if extra_collection_from in self.__cfg.collections:
                self.extra_collections.append((await self.__create_collection(extra_collection_from),))
            else:
                self.logs_buffer.write(f"warning: not found collection with id={extra_collection_from} in config (app id={self.app_id})\n")
                log_warn(f"warning: not found collection with id={extra_collection_from} in config (app id={self.app_id})")
                self.extra_collections.append(None)

        self.sink_collections = []
        if self.__sink_names is not None:
            for sink_name in self.__sink_names:
                if sink_name in self.__cfg.collections:
                    self.sink_collections.append((await self.__create_collection(sink_name),))
                else:
                    self.logs_buffer.write(f"warning: not found collection with id={sink_name} in config (app id={self.app_id})\n")
                    log_warn(f"warning: not found collection with id={sink_name} in config (app id={self.app_id})")
                    self.sink_collections.append(None)

    def _with_extra_collections(self) -> List[Tuple[Collection, ...]]:
        if self.__app_version > 0:
            if len(self.__extra_argnames) != len(self.extra_collections):
                raise EntityException(f"wrong extra collections count: len(extra argnames)={len(self.__extra_argnames)}, len(exrta collections)={len(self.extra_collections)}")
            collections = [None] * (len(self.__argnames) + len(self.extra_collections))

            sink_index = self.__schemes_info_processor[2]
            if sink_index is not None:
                if self.start_processor_context_pos():
                    sink_index -= 1
                sink_names_len = 0 if self.__sink_names is None else len(self.__sink_names)
                if self.state.is_init_app and sink_names_len == 0:
                    raise EntityException("sink app should not be first or sink names should set")
                sink_collections_len = len(self.collections) - len(self.__argnames) + 1
                if sink_collections_len + sink_names_len < 0:
                    raise EntityException("wrong sink count arguments")

                for index, collection in zip(self.__extra_argnames.values(), self.extra_collections):
                    collections[index] = collection

                shift = 0
                for i, index in enumerate(sorted(self.__argnames.values())):
                    if index == sink_index:
                        collections[index] = self.sink_collections + self.collections[i:i+sink_collections_len]
                        shift = sink_collections_len - 1
                    else:
                        collections[index] = self.collections[i+shift]

                collections = collections[:sink_index] + collections[sink_index] + collections[sink_index+1:]
            else:
                if len(self.__argnames) != len(self.collections):
                    raise EntityException(f"wrong collections count: len(argnames)={len(self.__argnames)}, len(collections)={len(self.collections)}")

                for index, collection in zip(self.__argnames.values(), self.collections):
                    collections[index] = collection

                for index, collection in zip(self.__extra_argnames.values(), self.extra_collections):
                    collections[index] = collection
            return collections
        else:
            return self.collections + self.extra_collections

    async def __create_collection(self, name: str) -> Collection:
        coll = self.__cfg.collections[name]
        try:
            if isinstance(coll, str):
                if coll.startswith(ObjectCollection.prefix):
                    return ObjectCollection(coll)
                return MongoCollection(coll, "check")
            elif "ref" in coll:     # FIXME not achievable ???
                path = f"{TEMP_FILES}/{name}"
                if "mode" not in coll:
                    raise Exception(f"wrong cfg: collection with name={name} must have ref mode")
                if coll["mode"] == "google_drive":
                    download_google_drive(coll["ref"], path)
                else:
                    raise Exception(f"wrong cfg: wrong mode in collection with name={name}")
                coll_mode = coll.get("drop_mode", "check")
                return FileCollection(path, self.__operation_id, mode=coll_mode)
            elif "query" in coll:
                query = coll["query"]
                if "credentials_id" in coll:
                    credentials = Credentials(operationId=self.__operation_id, credentialsId=coll["credentials_id"])
                    coll = await post_request_json(end.CREDENTIALS, credentials.model_dump_json(), buffer=self.logs_buffer)
                url, username, password = coll["url"], coll["username"], coll["password"]
                db_query = DBQuery(url=url, username=username, password=password, query=query)
                collection_outside = CollectionOutside(operationId=self.__operation_id, appId=self.app_id,
                                                       type=get_db_type_by_url(url), query=db_query, fixScheme=None)    # fix it
                coll_id = await post_request_json(end.OUTSIDE_COLLECTION, collection_outside.model_dump_json(), text=True, buffer=self.logs_buffer)
                coll_mode = coll.get("drop_mode", "check")
                return MongoCollection(coll_id, mode=coll_mode)
            else:
                raise Exception("wrong cfg collections mode")
        except Exception as ex:
            self.logs_buffer.write(f"error: {ex}\n")
            log_error(ex)
            raise ex

    def set_collections(self, colls: List[Tuple[Collection, ...]]):
        self.collections = colls

    def set_stream(self, f: callable):
        self.stream = f
        self.collections = []

    def set_extra_collections(self, colls: List[Tuple[Collection, ...]]):
        """only for kafka"""
        self.extra_collections = colls

    def prepare(self, in_id: str = None, proc_id: str = None, out_id: str = None, cond_id: str = None):
        self._input_id = in_id
        self._processor_id = proc_id
        self._output_id = out_id
        self._condition_id = cond_id
        self.__input_fun = None
        self.__processor_fun = None
        self.__output_fun = None
        self.__condition_fun = None
        self.collections.clear()
        self.extra_collections.clear()
        self.__init_funs.clear()

    def _validation(self):
        assert self.processor_fun_exists(), f"wrong processor id: {self._processor_id}"
        assert self._input_id is None or self.input_fun_exists(), f"wrong input id: {self._input_id}"
        assert self._output_id is None or self.output_fun_exists(), f"wrong output id: {self._output_id}"

    @property
    def need_drop_internal(self) -> bool:
        if self.__operation == EntityType.INPUT:
            return False
        elif self.__operation == EntityType.PROCESSOR:
            return self.__processor_drop_internal
        elif self.__operation == EntityType.OUTPUT:
            return self.__output_drop_internal
        elif self.__operation == EntityType.CONDITION:
            return self.__condition_drop_internal
        else:
            raise Exception("wrong operation, need drop internal")

    async def get_schemes_info(self) -> Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], Optional[int]]:
        if self.__operation == EntityType.INPUT:
            schemes_info, ret_type, sink_index = self.__schemes_info_input
        elif self.__operation == EntityType.PROCESSOR:
            schemes_info, ret_type, sink_index = self.__schemes_info_processor
        elif self.__operation == EntityType.OUTPUT:
            schemes_info, ret_type, sink_index = self.__schemes_info_output
        elif self.__operation == EntityType.CONDITION:
            schemes_info, ret_type, sink_index = self.__schemes_info_condition
        else:
            raise Exception("wrong operation, get scheme name")

        res = await gather(*map(lambda x: self.__update_schemes(x[1]), schemes_info))
        return [(x[0], res[i]) for i, x in enumerate(schemes_info)], ret_type, sink_index

    def __get_scheme(self, name: str) -> Optional[str]:
        return self.__schemes.get(name, None)

    async def __update_schemes_inside(self, scheme_name: Optional[str]) -> Optional[str]:
        if scheme_name is None or scheme_name == "*":
            return scheme_name
        elif isinstance(scheme_name, str):
            if scheme_name in self.__cfg.schemes_aliases:
                scheme_name = self.__cfg.schemes_aliases[scheme_name]
            if scheme_name in self.__schemes_send:
                return f"{self.__operation_id}_{scheme_name}"
            scheme = self.__get_scheme(scheme_name)
            if scheme is None:  # not defined with jls.scheme
                return scheme_name
            temp_run_scheme = TempRunScheme(operationId=self.__operation_id, data=scheme, name=scheme_name)
            if not self.__is_local:
                await post_request_json(end.RUN_SCHEME, temp_run_scheme.model_dump_json(), text=True, buffer=self.logs_buffer)
            self.__schemes_send.add(scheme_name)
            return f"{self.__operation_id}_{scheme_name}"
        self.logs_buffer.write(f"warn: wrong scheme type: {scheme_name}\n")
        return None

    async def __update_schemes(self, scheme_names: Optional[Tuple[Optional[str], ...]]) -> Optional[Tuple[Optional[str], ...]]:   # one argument
        if scheme_names is None:
            return scheme_names
        assert isinstance(scheme_names, Tuple), f"wrong scheme {scheme_names}"
        return tuple(await gather(*map(self.__update_schemes_inside, scheme_names)))

    def set_operation(self, operation: EntityType):
        self.__operation = operation

    def get_operation(self) -> EntityType:
        return self.__operation

    def __get_context_pos(self) -> ContextPosition:
        if self.__operation == EntityType.INPUT:
            return self.__input_context_pos
        elif self.__operation == EntityType.PROCESSOR:
            return self.__processor_context_pos
        elif self.__operation == EntityType.OUTPUT:
            return self.__output_context_pos
        elif self.__operation == EntityType.CONDITION:
            return self.__condition_context_pos
        else:
            raise Exception(f"wrong operation: {self.__operation.name}")

    def start_processor_context_pos(self) -> bool:
        return self.__processor_context_pos == ContextPosition.START

    def register_input(self, input_fun: callable, id: Optional[str], collection_from: Optional[str], collections_from: Optional[List[str]], extra_collection_from: Optional[str], extra_collections_from: Optional[List[str]], by_args: bool, query: Optional[str], finish_msg: Optional[str], cpu_bound: bool, tags: Dict[str, str], mode: InputWrapper):
        if id is None:
            id = input_fun.__name__
        if self.__mode == "info":
            self.__input_collection_from = collection_from
            self.__input_collections_from = collections_from
            self.__input_extra_collection_from = extra_collection_from
            self.__input_extra_collections_from = extra_collections_from
            self.__input_df_by_args = by_args
            collections_names = self.get_input_collections()
            extra_collections_names = self.get_extra_input_collections()
            if query is not None:
                if collections_names is not None or extra_collections_names is not None:
                    raise EntityException(f"only one way to set collections (app id={self.app_id})")
            if id not in self.__info.inputs:
                # try:
                input_function_info = InputFunctionInfo(id=id, name=input_fun.__name__, arguments=get_fun_info_verbose(input_fun), doc=input_fun.__doc__, collectionsNames=collections_names, extraCollectionsNames=extra_collections_names, query=query, finishMsg=finish_msg, cpuBound=cpu_bound, tags=tags, mode=mode.value)
                # except:
                #     self.logs_buffer.write(f"wrong input: {id}")
                #     input_function_info = InputFunctionInfo(id=id, name=input_fun.__name__, arguments=get_fun_info_verbose(input_fun), doc=input_fun.__doc__, collectionsNames=collections_names, extraCollectionsNames=extra_collections_names, query=query, finishMsg=finish_msg, cpuBound=cpu_bound, mode=mode.value)
                self.__info.inputs[id] = input_function_info
            else:
                return
        if id != self._input_id or (self.__mode != "info" and self.input_fun_exists()):
            return
        schemes_info = get_fun_info(input_fun)
        self.__input_mode = mode
        self.__input_fun = input_fun
        self.__input_cpu_bound = cpu_bound
        if len(schemes_info[0]) > 0:
            context_fun = None
            if schemes_info[0][0][1] == CONTEXT:
                self.__input_context_pos = ContextPosition.START
                context_fun = schemes_info[0][0][0]
                schemes_info[0].pop(0)
            elif schemes_info[0][-1][1] == CONTEXT:
                self.__input_context_pos = ContextPosition.END
                context_fun = schemes_info[0][-1][0]
                schemes_info[0].pop()
            if context_fun is not None:
                context_fun_name = get_model_name(context_fun)
                self.__fun_id_to_context_param[id] = context_fun_name
                if context_fun_name not in self.__context_funcs:
                    self.__context_funcs[context_fun_name] = context_fun
        self._update_schemes_info(schemes_info, EntityType.INPUT)

        if query is not None:
            if collection_from is not None or collections_from is not None:
                raise EntityException(f"only one way to set collections (app id={self.app_id})")
            query_collection = QueryCollection(operationId=self.__operation_id, query=query)
            collection_from = asyncio.run(post_request_json(end.QUERY, query_collection.model_dump_json(), text=True, buffer=self.logs_buffer))
        self.__input_collection_from = collection_from
        self.__input_collections_from = collections_from
        self.__input_extra_collection_from = extra_collection_from
        self.__input_extra_collections_from = extra_collections_from
        self.__input_df_by_args = by_args
        self.__input_finish_msg = finish_msg
        self.__set_collections()

    def register_processor(self, processor_fun: callable, id: Optional[str], finish_msg: Optional[str], cpu_bound: bool, is_stream: bool, tags: Dict[str, str], drop_internal: bool, get_scale_part_all: bool = False):
        if id is None:
            id = processor_fun.__name__
        schemes_info = None
        if self.__mode == "info":
            if id not in self.__info.processors:
                schemes_info = get_fun_info(processor_fun)
                # try:
                processor_function_info = ProcessorFunctionInfo(id=id, name=processor_fun.__name__, arguments=get_fun_info_verbose(processor_fun), doc=processor_fun.__doc__, finishMsg=finish_msg, cpuBound=cpu_bound, isStream=is_stream, tags=tags, contextClass=get_context_info(schemes_info[0]))
                # except:
                #     self.logs_buffer.write(f"wrong processor: {id}")
                #     processor_function_info = ProcessorFunctionInfo(id=id, name=processor_fun.__name__, arguments=get_fun_info_verbose(processor_fun), doc=processor_fun.__doc__, finishMsg=finish_msg, cpuBound=cpu_bound, isStream=is_stream, contextClass=get_context_info(schemes_info[0]))
                self.__info.processors[id] = processor_function_info
            else:
                return
        if id != self._processor_id or (self.__mode != "info" and self.processor_fun_exists()):
            return
        if self.__mode != "info":
            schemes_info = get_fun_info(processor_fun)
        self.__processor_fun = processor_fun
        self.__processor_cpu_bound = cpu_bound
        self.__processor_is_stream = is_stream
        if len(schemes_info[0]) > 0:
            context_fun = None
            if schemes_info[0][0][1] == CONTEXT:
                self.__processor_context_pos = ContextPosition.START
                context_fun = schemes_info[0][0][0]
                schemes_info[0].pop(0)
            elif schemes_info[0][-1][1] == CONTEXT:
                self.__processor_context_pos = ContextPosition.END
                context_fun = schemes_info[0][-1][0]
                schemes_info[0].pop()
            if context_fun is not None:
                context_fun_name = get_model_name(context_fun)
                self.__fun_id_to_context_param[id] = context_fun_name
                if context_fun_name not in self.__context_funcs:
                    self.__context_funcs[context_fun_name] = context_fun
        self.__processor_finish_msg = finish_msg
        self.__processor_drop_internal = drop_internal
        self.__processor_get_scale_part_all = get_scale_part_all
        self._update_schemes_info(schemes_info, EntityType.PROCESSOR)

    def register_output(self, output_fun: callable, id: Optional[str], collection_out_name: Optional[str], collection_out_names: Optional[List[str]], finish_msg: Optional[str], cpu_bound: bool, tags: Dict[str, str], drop_internal: bool):
        if id is None:
            id = output_fun.__name__
        assert collection_out_name is None or collection_out_names is None, f"only one way to set out collection names (app id={self.app_id}), use collection_name or collection_names"
        if collection_out_name is not None:
            collection_out_names = [collection_out_name]
        if self.__mode == "info":
            if id not in self.__info.outputs:
                # try:
                output_function_info = OutputFunctionInfo(id=id, name=output_fun.__name__, arguments=get_fun_info_verbose(output_fun), doc=output_fun.__doc__, collectionOutNames=collection_out_names, finishMsg=finish_msg, cpuBound=cpu_bound, tags=tags)
                # except:
                #     self.logs_buffer.write(f"wrong output: {id}")
                #     output_function_info = OutputFunctionInfo(id=id, name=output_fun.__name__, arguments=get_fun_info_verbose(output_fun), doc=output_fun.__doc__, collectionOutNames=collection_out_names, finishMsg=finish_msg, cpuBound=cpu_bound)
                self.__info.outputs[id] = output_function_info
            else:
                return
        if id != self._output_id or (self.__mode != "info" and self.output_fun_exists()):
            return
        schemes_info = get_fun_info(output_fun)
        self.__output_fun = output_fun
        self.__output_cpu_bound = cpu_bound
        if len(schemes_info[0]) > 0:
            context_fun = None
            if schemes_info[0][0][1] == CONTEXT:
                self.__output_context_pos = ContextPosition.START
                context_fun = schemes_info[0][0][0]
                schemes_info[0].pop(0)
            elif schemes_info[0][-1][1] == CONTEXT:
                self.__output_context_pos = ContextPosition.END
                context_fun = schemes_info[0][-1][0]
                schemes_info[0].pop()
            if context_fun is not None:
                context_fun_name = get_model_name(context_fun)
                self.__fun_id_to_context_param[id] = context_fun_name
                if context_fun_name not in self.__context_funcs:
                    self.__context_funcs[context_fun_name] = context_fun
        self._update_schemes_info(schemes_info, EntityType.OUTPUT)
        if collection_out_names is not None:
            self.collection_out_names = []
            for collection_out_name in collection_out_names:
                override_name = self.__cfg.different.get(collection_out_name)
                if override_name is not None:
                    collection_out_name = override_name
                self.collection_out_names.append(collection_out_name)
        self.__output_finish_msg = finish_msg
        self.__output_drop_internal = drop_internal

    def register_condition(self, condition_fun: callable, id: Optional[str], finish_msg: Optional[str], cpu_bound: bool, tags: Dict[str, str], drop_internal: bool):
        if id is None:
            id = condition_fun.__name__
        if self.__mode == "info":
            if id not in self.__info.conditions:
                # try:
                condition_function_info = ConditionFunctionInfo(id=id, name=condition_fun.__name__, arguments=get_fun_info_verbose(condition_fun), doc=condition_fun.__doc__, finishMsg=finish_msg, cpuBound=cpu_bound, tags=tags)
                # except:
                #     self.logs_buffer.write(f"wrong condition: {id}")
                #     condition_function_info = ConditionFunctionInfo(id=id, name=condition_fun.__name__, arguments=get_fun_info_verbose(condition_fun), doc=condition_fun.__doc__, finishMsg=finish_msg, cpuBound=cpu_bound)
                self.__info.conditions[id] = condition_function_info
            else:
                return
        if id != self._condition_id or (self.__mode != "info" and self.condition_fun_exists()):
            return
        schemes_info = get_fun_info(condition_fun)
        self.__condition_fun = condition_fun
        self.__condition_cpu_bound = cpu_bound
        if len(schemes_info[0]) > 0:
            context_fun = None
            if schemes_info[0][0][1] == CONTEXT:
                self.__condition_context_pos = ContextPosition.START
                context_fun = schemes_info[0][0][0]
                schemes_info[0].pop(0)
            elif schemes_info[0][-1][1] == CONTEXT:
                self.__condition_context_pos = ContextPosition.END
                context_fun = schemes_info[0][-1][0]
                schemes_info[0].pop()
            if context_fun is not None:
                context_fun_name = get_model_name(context_fun)
                self.__fun_id_to_context_param[id] = context_fun_name
                if context_fun_name not in self.__context_funcs:
                    self.__context_funcs[context_fun_name] = context_fun
        self.__condition_finish_msg = finish_msg
        self.__condition_drop_internal = drop_internal
        self._update_schemes_info(schemes_info, EntityType.CONDITION)

    def register_scheme(self, cl: BaseModel, name: Optional[str] = None):
        if name is None:
            name = cl.__name__
        scheme = json_schema(cl)
        if self.__mode == "info":
            self.__info.schemes[name] = scheme
        self.__exist_schemes.add(f"{self.__operation_id}_{name}")
        self.__schemes[name] = scheme

    def is_internal_scheme(self, name: str) -> bool:
        return name.removeprefix(f"{self.operation_id}_") in self.__schemes     # FIXME make it neater

    def register_init(self, init_fun: callable, id: Optional[str], enable: bool, tl: Optional[int], prepare: bool, cpu_bound: bool, tags: Dict[str, str]):
        if self.__app_version < 2 and ((self.__mode == "init" and not prepare) or (self.__mode == "run" and prepare)):
            return
        if id is None:
            id = init_fun.__name__
        init_apps_update = self.__cfg.init_apps_update if self.__cfg is not None else {}    # for info mode
        if id in init_apps_update:
            enable = init_apps_update[id]
        if self.__mode == "info":
            # try:
            init_function_info = InitInfo(id=id, enable=enable, tl=tl, prepare=prepare, argname=get_context_argname(init_fun), doc=init_fun.__doc__, cpuBound=cpu_bound, tags=tags)
            # except:
            #     self.logs_buffer.write(f"wrong init: {id}")
            #     init_function_info = InitInfo(id=id, enable=enable, tl=tl, prepare=prepare, argname=get_context_argname(init_fun), doc=init_fun.__doc__, cpuBound=cpu_bound)
            self.__info.inits[id] = init_function_info
        if not enable:
            return

        count = get_argcount(init_fun)
        assert count <= 1, f"wrong init arguments: expected zero or one (Context), found {count}"
        if count == 1:
            varname = get_argnames(init_fun)[0]
            context_fun = get_annotations(init_fun).get(varname, None)
            assert getattr(context_fun, "__name__", None) == CONTEXT_TYPE or getattr(context_fun, "__origin__", None) is Context, f"wrong type in init: {context_fun}"
            context_fun_name = get_model_name(context_fun)
            self.__fun_id_to_context_param[id] = context_fun_name
            if context_fun_name not in self.__context_funcs:
                self.__context_funcs[context_fun_name] = context_fun
        if self.__app_version >= 2:
            if prepare:
                self.__init_funs_first.append(InitFunState(self, init_fun, id, tl, cpu_bound))
            else:
                self.__init_funs.append(InitFunState(self, init_fun, id, tl, cpu_bound))
        else:
            self.__init_funs.append(InitFunState(self, init_fun, id, tl, cpu_bound))

    async def __init_fail(self, fun_id: str, e: BaseException, trace: str):
        if not C.IS_LOCAL and C.WS is None:  # TODO allow for ws
            err_type = type(e).__name__
            err_args = [str(arg) for arg in e.args]
            is_malevich_err = isinstance(e, MalevichException)
            struct = fail_structure(self, self.__operation_id, self.run_id, "", 0, False, trace, err_type, err_args, is_malevich_err, self._cfg_dict_if_need(), init_fun_id=fun_id)
            await post_error_info(struct, self.logs_buffer)

    async def init_all(self) -> bool:
        try:
            self.__cur_task = gather(*[init_fun.run() for init_fun in self.__init_funs])
            await self.__cur_task
            return True
        except InitFunError as e:
            trace = format_exc_skip(skip=3)
            self.logs_buffer.write(f"init failed: {trace}\n")
            await self.__init_fail(e.fun_id, e.__cause__, trace)
            return False
        except BaseException as e:
            trace = format_exc_skip(skip=2)
            self.logs_buffer.write(f"init failed: {trace}\n")
            await self.__init_fail("", e, trace)
            return False
        finally:
            self.__cur_task = None

    async def init_all_first(self) -> bool:
        try:
            await gather(*[init_fun.run() for init_fun in self.__init_funs_first])
            return True
        except InitFunError as e:
            trace = format_exc_skip(skip=3)
            self.logs_buffer.write(f"start init failed: {trace}\n")
            await self.__init_fail(e.fun_id, e.__cause__, trace)
            return False
        except BaseException as e:
            trace = format_exc_skip(skip=2)
            self.logs_buffer.write(f"start init failed: {trace}\n")
            await self.__init_fail("", e, trace)
            return False

    def _update_schemes_info(self, schemes_info: Tuple[List[Tuple[Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], Optional[Any], bool], operation: EntityType):
        if operation == EntityType.INPUT:
            self.__schemes_info_input = schemes_info
        elif operation == EntityType.PROCESSOR:
            self.__schemes_info_processor = schemes_info
        elif operation == EntityType.OUTPUT:
            self.__schemes_info_output = schemes_info
        elif operation == EntityType.CONDITION:
            self.__schemes_info_condition = schemes_info
        else:
            raise Exception("wrong operation, update scheme info")

    async def __input(self, *args):
        try:
            self.__cur_task = asyncio.create_task(run_func(self.__input_fun, *args, cpu_bound=self.__input_cpu_bound, logs_buffer=self.logs_buffer))
            res = await self.__cur_task
            if self.__input_finish_msg is not None:
                self._context.email_send(message=self.__input_finish_msg, subject=FINISH_SUBJ)
            return True, res
        except BaseException as e:
            form_exc = format_exc_skip(skip=2)
            if not self.__input_cpu_bound:
                self.logs_buffer.write(f"{form_exc}\n")
            log_error(form_exc)
            return False, (form_exc, type(e).__name__, [str(arg) for arg in e.args], isinstance(e, MalevichException))
        finally:
            self.__cur_task = None

    def input_fun_exists(self):
        return self.__input_fun is not None

    async def __processor(self, *args):
        try:
            self.__cur_task = asyncio.create_task(run_func(self.__processor_fun, *args, cpu_bound=self.__processor_cpu_bound, logs_buffer=self.logs_buffer))
            res = await self.__cur_task
            if self.__processor_finish_msg is not None:
                self._context.email_send(message=self.__processor_finish_msg, subject=FINISH_SUBJ)
            return True, res
        except BaseException as e:
            form_exc = format_exc_skip(skip=2)
            if not self.__processor_cpu_bound:
                self.logs_buffer.write(f"{form_exc}\n")
            log_error(form_exc)
            return False, (form_exc, type(e).__name__, [str(arg) for arg in e.args], isinstance(e, MalevichException))
        finally:
            self.__cur_task = None

    def processor_fun_exists(self):
        return self.__processor_fun is not None

    async def __output(self, *args):
        try:
            self.__cur_task = asyncio.create_task(run_func(self.__output_fun, *args, cpu_bound=self.__output_cpu_bound, logs_buffer=self.logs_buffer))
            res = await self.__cur_task
            if self.__output_finish_msg is not None:
                self._context.email_send(message=self.__output_finish_msg, subject=FINISH_SUBJ)
            return True, res
        except BaseException as e:
            form_exc = format_exc_skip(skip=2)
            if not self.__output_cpu_bound:
                self.logs_buffer.write(f"{form_exc}\n")
            log_error(form_exc)
            return False, (form_exc, type(e).__name__, [str(arg) for arg in e.args], isinstance(e, MalevichException))
        finally:
            self.__cur_task = None

    def output_fun_exists(self):
        return self.__output_fun is not None

    async def __condition(self, *args):
        try:
            self.__cur_task = asyncio.create_task(run_func(self.__condition_fun, *args, cpu_bound=self.__condition_cpu_bound, logs_buffer=self.logs_buffer))
            res = await self.__cur_task
            if self.__condition_finish_msg is not None:
                self._context.email_send(message=self.__condition_finish_msg, subject=FINISH_SUBJ)
            if isinstance(res, Tuple) and len(res) == 1:
                fixed_res = res[0]
            else:
                fixed_res = res
            assert isinstance(fixed_res, bool) or isinstance(res, numpy.bool_), f"wrong condition function result type: {type(res)} (expected bool or Tuple[bool])" # TODO add bool alternatives
            return True, bool(fixed_res)
        except BaseException as e:
            form_exc = format_exc_skip(skip=2)
            if not self.__condition_cpu_bound:
                self.logs_buffer.write(f"{form_exc}\n")
            log_error(form_exc)
            return False, (form_exc, type(e).__name__, [str(arg) for arg in e.args], isinstance(e, MalevichException))
        finally:
            self.__cur_task = None

    def condition_fun_exists(self):
        return self.__condition_fun is not None

    def __fun_and_id(self) -> Tuple[callable, str]:
        if self.__operation == EntityType.INPUT:
            run_fun = self.__input
            fun_id = self._input_id
        elif self.__operation == EntityType.PROCESSOR:
            run_fun = self.__processor
            fun_id = self._processor_id
        elif self.__operation == EntityType.OUTPUT:
            run_fun = self.__output
            fun_id = self._output_id
        elif self.__operation == EntityType.CONDITION:
            run_fun = self.__condition
            fun_id = self._condition_id
        else:
            raise Exception(f"wrong operation: {self.__operation.name}")
        return run_fun, fun_id

    def is_stream(self) -> bool:
        return self.__processor_is_stream

    def _cfg_dict_if_need(self, fun_id: Optional[str] = None) -> Dict[str, Any]: # maybe cfg is wrong because it is already used
        if self.__get_context_pos() == ContextPosition.NONE:
            return None
        if fun_id is None:
            _, fun_id = self.__fun_and_id()
        context = self._get_context(fun_id)
        app_cfg = context.app_cfg
        if isinstance(app_cfg, BaseModel):
            app_cfg = app_cfg.model_dump()
        return app_cfg

    async def run(self, *args) -> Tuple[bool, Any]: # Any - colls or Tuple[str, str, List[str], bool]
        run_fun, fun_id = self.__fun_and_id()
        self.profile_mode.run_start(*args, fun_id=fun_id, buffer=self.logs_buffer)

        context_pos = self.__get_context_pos()
        if context_pos == ContextPosition.START:
            args = [self._get_context(fun_id), *args]
        elif context_pos == ContextPosition.END:
            args = [*args, self._get_context(fun_id)]

        with redirect_out(self.logs_buffer):
            res = await run_fun(*args)

        if res[0]:
            self.profile_mode.run_end(res[1], fun_id=fun_id, buffer=self.logs_buffer)
        if self.__operation == EntityType.PROCESSOR and res[0] and res[1] is None:
            self.logs_buffer.write("error: processor function should return dataframes, not None\n")
            log_error("processor function should return dataframes, not None")
            res = (False, ("processor function should return dataframes, not None", "InternalError", [], False))
        return res

    def cancel(self):
        if self.__cur_task is not None:
            self.__cur_task.cancel()
