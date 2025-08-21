from __future__ import annotations
import base64
import importlib
import io
import logging
import os
import asyncio
from functools import cached_property
from uuid import uuid4
import requests
import pickle
import shutil
import traceback
import aiohttp
import json
import jsonpickle
from pathlib import Path
from asyncio import gather
from typing import Optional, Any, List, Dict, Union, Tuple, TypeVar, Generic, Callable, Coroutine
import pandas as pd
import numpy as np
from pydantic import BaseModel
from pydantic.v1.json import pydantic_encoder
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import Keys, KeysValues, Info, Message, OperationWithRunWithKey, \
    OperationWithRun, \
    OSGetBatch, OSGetAll, OSGetKeys, SynchronizeSettings, KeysPresigned, Presigned, KeysWithSynchronize, ObjectRequest, \
    KVPostRawValuesDataRequest
from malevich_app.export.jls.LocalLogsBuffer import LocalLogsBuffer
from malevich_app.export.jls.df import OBJ, JDF, DFS, Sink, Docs, DF
from malevich_app.export.request.dag_requests import send_post_dag, send_delete_dag
from malevich_app.export.secondary.LogHelper import log_info, log_error, log_warn
from malevich_app.export.secondary.endpoints import GET_KEYS_VALUES_RAW, GET_KEYS_VALUES, GET_KEYS_VALUES_ALL, POST_KEYS_VALUES_RAW, \
    POST_KEYS_VALUES, DELETE_KEYS_VALUES_ALL, GET_OBJ_STORAGE, GET_OBJ_STORAGE_ALL, POST_OBJ_STORAGE, \
    DELETE_OBJ_STORAGE, MESSAGE, GET_OBJ_STORAGE_KEYS, SYNCHRONIZE, POST_PRESIGNED_OBJ_STORAGE, OBJECTS
from malevich_app.export.secondary.helpers import send_background_task, merge_move_dir
from malevich_app.export.secondary.logger import context_logger
from malevich_app.export.secondary.zip import zip_raw
from malevich_app.export.secondary.pause import Pause
from malevich_app.jls_lib.s3_utils import S3Helper
from malevich_app.jls_lib.senders_utils import SmtpSender

WORKDIR = C.WORKDIR
APP_DIR = C.APP_DIR
_ = S3Helper
_ = SmtpSender
MinimalCfg = TypeVar('MinimalCfg')


def _dict_with_class(base):
    assert (hasattr(base, "__orig_class__") and hasattr(base.__orig_class__, "__args__") and len(base.__orig_class__.__args__) == 1), "wrong app_cfg extension class type"
    arg = base.__orig_class__.__args__[0]
    module_name, name = arg.__module__, arg.__name__
    assert not (module_name == "builtins" and name == "NoneType"), "app_cfg extension: expected class, not None"

    module = importlib.import_module(module_name)
    cl = getattr(module, name)
    assert issubclass(cl, BaseModel), "app_cfg extension: class should be subclass of BaseModel"

    class Wrapper(cl):
        def __init__(self, data):
            super().__init__(**data)
            self.__data = data

        def clear(self):
            self.__data.clear()

        def copy(self, *args, **kwargs):
            return Wrapper(self.__data.copy(*args, **kwargs))

        def get(self, *args, **kwargs):
            return self.__data.get(*args, **kwargs)

        def items(self):
            return self.__data.items()

        def keys(self):
            return self.__data.keys()

        def pop(self, k, d=None):
            return self.__data.pop(k, d)

        def popitem(self, *args, **kwargs):
            return self.__data.popitem(*args, **kwargs)

        def setdefault(self, *args, **kwargs):
            return self.__data.setdefault(*args, **kwargs)

        def update(self, E=None, **F):
            return self.__data.update(E, **F)

        def values(self):
            return self.__data.values()

        def __contains__(self, *args, **kwargs):
            return self.__data.__contains__(*args, **kwargs)

        def __delitem__(self, *args, **kwargs):
            return self.__data.__delitem__(*args, **kwargs)

        def __eq__(self, *args, **kwargs):  # not BaseModel eq
            return self.__data.__eq__(*args, **kwargs)

        def __getitem__(self, y):
            return self.__data.__getitem__(y)

        def __ge__(self, *args, **kwargs):
            return self.__data.__ge__(*args, **kwargs)

        def __gt__(self, *args, **kwargs):
            return self.__data.__gt__(*args, **kwargs)

        def __ior__(self, *args, **kwargs):
            return self.__data.__ior__(*args, **kwargs)

        def __iter__(self, *args, **kwargs):
            return self.__data.__iter__(*args, **kwargs)

        def __len__(self, *args, **kwargs):
            return self.__data.__len__(*args, **kwargs)

        def __le__(self, *args, **kwargs):
            return self.__data.__le__(*args, **kwargs)

        def __lt__(self, *args, **kwargs):
            return self.__data.__lt__(*args, **kwargs)

        def __ne__(self, *args, **kwargs):
            return self.__data.__ne__(*args, **kwargs)

        def __or__(self, *args, **kwargs):
            return self.__data.__or__(*args, **kwargs)

        def __repr__(self, *args, **kwargs):
            return self.__data.__repr__(*args, **kwargs)

        __str__ = __repr__

        def __reversed__(self, *args, **kwargs):
            return self.__data.__reversed__(*args, **kwargs)

        def __ror__(self, *args, **kwargs):
            return self.__data.__ror__(*args, **kwargs)

        def __setitem__(self, *args, **kwargs):
            return self.__data.__setitem__(*args, **kwargs)

        def __sizeof__(self):
            return self.__data.__sizeof__()

        def dict(self, *args, **kwargs):
            return self.__data

        def to_dict(self):
            return self.__data

        __hash__ = None

    Wrapper.__name__ = cl.__name__
    Wrapper.__doc__ = cl.__doc__
    Wrapper.__annotations__ = cl.__annotations__
    return Wrapper


def _async_run(f: Coroutine):
    if C.WS_LOOP is None:
        return asyncio.run(f)
    else:
        asyncio.set_event_loop(C.WS_LOOP)
        return C.WS_LOOP.run_until_complete(f)


class Context(Generic[MinimalCfg]):
    class _DagKeyValue:
        """values must be bytes, string, int or float; dictionary order is not guaranteed"""
        def __init__(self, operation_id: str, run_id: Optional[str], dag_host_port: str, secret: str, local_storage: Optional['LocalStorage']):
            self.__operation_id = operation_id
            self.__run_id = None    # run_id    # FIXME
            self.__dag_host_port = dag_host_port
            self.__secret = secret
            self.__is_local = local_storage is not None
            self.__local_storage = local_storage

        async def __get_bytes(self, key: str) -> bytes:
            operation = OperationWithRunWithKey(operationId=self.__operation_id, runId=self.__run_id, key=key, hostedAppId=C.APP_ID, secret=self.__secret)
            return await send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES_RAW(self.__dag_host_port), raw_res=True,
                                       headers={'Content-type': 'application/json', 'Accept': 'application/python-pickle'}, operation_id=self.__operation_id)

        def __get_bytes2(self, key: str) -> bytes:
            operation = OperationWithRunWithKey(operationId=self.__operation_id, runId=self.__run_id, key=key, hostedAppId=C.APP_ID, secret=self.__secret)
            return _async_run(send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES_RAW(self.__dag_host_port), raw_res=True,
                                       headers={'Content-type': 'application/json', 'Accept': 'application/python-pickle'}, operation_id=self.__operation_id))

        async def __fix_get(self, keys_values: Dict[str, Any]) -> Dict[str, Any]:
            keys = []
            values = []
            for k, v in keys_values.items():
                if v is None:
                    keys.append(k)
                    values.append(self.__get_bytes(k))
            for k, v in zip(keys, await gather(*values)):
                keys_values[k] = v
            return keys_values

        def __fix_get2(self, keys_values: Dict[str, Any]) -> Dict[str, Any]:
            keys = []
            values = []
            for k, v in keys_values.items():
                if v is None:
                    keys.append(k)
                    values.append(self.__get_bytes2(k))
            for k, v in zip(keys, values):
                keys_values[k] = v
            return keys_values

        def get_bytes(self, key: str) -> bytes:
            """a more optimal way to get a binary value by key (\"get\" can also be used)"""
            if self.__is_local:
                return self.__local_storage.kv.get_bytes(self.__operation_id, self.__run_id, key)
            return self.__get_bytes2(key)

        async def async_get_bytes(self, key: str) -> bytes:
            """a more optimal way to get a binary value by key (\"get\" can also be used)"""
            if self.__is_local:
                return self.__local_storage.kv.get_bytes(self.__operation_id, self.__run_id, key)
            return await self.__get_bytes(key)

        def get(self, keys: List[str]) -> Dict[str, Any]:
            if self.__is_local:
                return self.__local_storage.kv.get(self.__operation_id, self.__run_id, keys)
            operation = Keys(operationId=self.__operation_id, data=keys, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            res = _async_run(send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES(self.__dag_host_port), operation_id=self.__operation_id))
            return self.__fix_get2(res)

        async def async_get(self, keys: List[str]) -> Dict[str, Any]:
            if self.__is_local:
                return self.__local_storage.kv.get(self.__operation_id, self.__run_id, keys)
            operation = Keys(operationId=self.__operation_id, data=keys, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            res = await send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES(self.__dag_host_port), operation_id=self.__operation_id)
            return await self.__fix_get(res)

        def get_all(self) -> Dict[str, Any]:
            if self.__is_local:
                return self.__local_storage.kv.get_all(self.__operation_id, self.__run_id)
            operation = OperationWithRun(operationId=self.__operation_id, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            res = _async_run(send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES_ALL(self.__dag_host_port), operation_id=self.__operation_id))
            return self.__fix_get2(res)

        async def async_get_all(self) -> Dict[str, Any]:
            if self.__is_local:
                return self.__local_storage.kv.get_all(self.__operation_id, self.__run_id)
            operation = OperationWithRun(operationId=self.__operation_id, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            res = await send_post_dag(operation.model_dump_json(), GET_KEYS_VALUES_ALL(self.__dag_host_port), operation_id=self.__operation_id)
            return await self.__fix_get(res)

        async def __update(self, keys_values: Dict[str, Any]):
            main_keys_values = dict()
            sends = []
            for k, v in keys_values.items():
                if isinstance(v, bytes):
                    run_id_part = f"/{self.__run_id}" if self.__run_id is not None else ""
                    if C.WS is not None:
                        payload = base64.b64encode(v).decode('utf-8')
                        v = KVPostRawValuesDataRequest(
                            operationId=self.__operation_id,
                            runId=self.__run_id,
                            hostedAppId=C.APP_ID,
                            key=k,
                            payload=payload,
                        )
                        url = POST_KEYS_VALUES_RAW(self.__dag_host_port)
                    else:
                        url = f"{POST_KEYS_VALUES_RAW(self.__dag_host_port)}/{k}/{C.APP_ID}/{self.__operation_id}{run_id_part}"
                    sends.append(send_post_dag(v, url, headers={'Content-type': 'application/python-pickle', 'Accept': 'application/json'}, operation_id=self.__operation_id))    # TODO secret
                else:
                    main_keys_values[k] = v
            if len(main_keys_values) > 0:
                operation = KeysValues(operationId=self.__operation_id, data=main_keys_values, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
                sends.append(send_post_dag(operation.model_dump_json(), POST_KEYS_VALUES(self.__dag_host_port), operation_id=self.__operation_id))
            await gather(*sends)

        def __update2(self, keys_values: Dict[str, Any]):
            main_keys_values = dict()
            for k, v in keys_values.items():
                if isinstance(v, bytes):
                    run_id_part = f"/{self.__run_id}" if self.__run_id is not None else ""
                    if C.WS is not None:
                        payload = base64.b64encode(v).decode('utf-8')
                        v = KVPostRawValuesDataRequest(
                            operationId=self.__operation_id,
                            runId=self.__run_id,
                            hostedAppId=C.APP_ID,
                            key=k,
                            payload=payload,
                        )
                        url = POST_KEYS_VALUES_RAW(self.__dag_host_port)
                    else:
                        url = f"{POST_KEYS_VALUES_RAW(self.__dag_host_port)}/{k}/{C.APP_ID}/{self.__operation_id}{run_id_part}"
                    _async_run(send_post_dag(v, url, headers={'Content-type': 'application/python-pickle', 'Accept': 'application/json'}, operation_id=self.__operation_id))     # TODO secret
                else:
                    main_keys_values[k] = v
            if len(main_keys_values) > 0:
                operation = KeysValues(operationId=self.__operation_id, data=main_keys_values, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
                _async_run(send_post_dag(operation.model_dump_json(), POST_KEYS_VALUES(self.__dag_host_port), operation_id=self.__operation_id))

        def update(self, keys_values: Dict[str, Any]) -> None:
            if self.__is_local:
                return self.__local_storage.kv.update(self.__operation_id, self.__run_id, keys_values)
            self.__update2(keys_values)

        async def async_update(self, keys_values: Dict[str, Any]) -> None:
            if self.__is_local:
                return self.__local_storage.kv.update(self.__operation_id, self.__run_id, keys_values)
            await self.__update(keys_values)

        def clear(self) -> None:
            if self.__is_local:
                return self.__local_storage.kv.clear(self.__operation_id, self.__run_id)
            operation = OperationWithRun(operationId=self.__operation_id, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            _async_run(send_delete_dag(operation.model_dump_json(), DELETE_KEYS_VALUES_ALL(self.__dag_host_port), operation_id=self.__operation_id))

        async def async_clear(self) -> None:
            if self.__is_local:
                return self.__local_storage.kv.clear(self.__operation_id, self.__run_id)
            operation = OperationWithRun(operationId=self.__operation_id, runId=self.__run_id, hostedAppId=C.APP_ID, secret=self.__secret)
            await send_delete_dag(operation.model_dump_json(), DELETE_KEYS_VALUES_ALL(self.__dag_host_port), operation_id=self.__operation_id)

    class _ObjectStorage:
        def __init__(self, operation_id: str, dag_host_port: str, secret: str, single_pod: bool, local_storage: Optional['LocalStorage']):
            self.__operation_id = operation_id
            self.__dag_host_port = dag_host_port
            self.__secret = secret
            self.__single_pod = single_pod
            self.__is_local = local_storage is not None
            self.__local_storage = local_storage

        def get_keys(self, local: bool = False, all_apps: bool = False) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = OSGetKeys(operationId=self.__operation_id, local=local, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = _async_run(send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE_KEYS(self.__dag_host_port), operation_id=self.__operation_id))
            return res["result"]

        async def async_get_keys(self, local: bool = False, all_apps: bool = False) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = OSGetKeys(operationId=self.__operation_id, local=local, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = await send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE_KEYS(self.__dag_host_port), operation_id=self.__operation_id)
            return res["result"]

        def get(self, keys: List[str], force: bool = False, all_apps: bool = True) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            if all_apps and not self.__single_pod and not force:
                log_warn("set force=True", context_logger)
                force = True
            operation = OSGetBatch(operationId=self.__operation_id, data=keys, force=force, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = _async_run(send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id))
            return res["result"]

        async def async_get(self, keys: List[str], force: bool = False, all_apps: bool = True) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            if all_apps and not self.__single_pod and not force:
                log_warn("set force=True", context_logger)
                force = True
            operation = OSGetBatch(operationId=self.__operation_id, data=keys, force=force, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = await send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id)
            return res["result"]

        def get_all(self, local: bool = False, force: bool = False, all_apps: bool = True) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            if not local and all_apps and not self.__single_pod and not force:
                log_warn("set force=True", context_logger)
                force = True
            elif local and not self.__single_pod and all_apps:
                log_warn("set all_apps=False", context_logger)
                all_apps = False
            operation = OSGetAll(operationId=self.__operation_id, local=local, force=force, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = _async_run(send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE_ALL(self.__dag_host_port), operation_id=self.__operation_id))
            return res["result"]

        async def async_get_all(self, local: bool = False, force: bool = False, all_apps: bool = True) -> List[str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            if not local and all_apps and not self.__single_pod and not force:
                log_warn("set force=True", context_logger)
                force = True
            elif local and not self.__single_pod and all_apps:
                log_warn("set all_apps=False", context_logger)
                all_apps = False
            operation = OSGetAll(operationId=self.__operation_id, local=local, force=force, hostedAppId=C.APP_ID, secret=self.__secret, allApps=all_apps)
            res = await send_post_dag(operation.model_dump_json(), GET_OBJ_STORAGE_ALL(self.__dag_host_port), operation_id=self.__operation_id)
            return res["result"]

        def update(self, keys: List[str], presigned_expire: Optional[int] = -1) -> Dict[str, str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = KeysPresigned(operationId=self.__operation_id, data=keys, presigned=presigned_expire, hostedAppId=C.APP_ID, secret=self.__secret)
            res = _async_run(send_post_dag(operation.model_dump_json(), POST_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id))
            return res["result"]

        async def async_update(self, keys: List[str], presigned_expire: Optional[int] = -1) -> Dict[str, str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = KeysPresigned(operationId=self.__operation_id, data=keys, presigned=presigned_expire, hostedAppId=C.APP_ID, secret=self.__secret)
            res = await send_post_dag(operation.model_dump_json(), POST_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id)
            return res["result"]

        def presigned(self, keys: List[str], expire: Optional[int] = None) -> Dict[str, str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            assert expire is None or expire >= 0, "expire value should be >= 0 or None"
            operation = Presigned(operationId=self.__operation_id, data=keys, presigned=expire, hostedAppId=C.APP_ID, secret=self.__secret)
            res = _async_run(send_post_dag(operation.model_dump_json(), POST_PRESIGNED_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id))
            return res["result"]

        async def async_presigned(self, keys: List[str], expire: Optional[int] = None) -> Dict[str, str]:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            assert expire is None or expire >= 0, "expire value should be >= 0 or None"
            operation = Presigned(operationId=self.__operation_id, data=keys, presigned=expire, hostedAppId=C.APP_ID, secret=self.__secret)
            res = await send_post_dag(operation.model_dump_json(), POST_PRESIGNED_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id)
            return res["result"]

        def delete(self, keys: List[str]) -> None:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = KeysWithSynchronize(operationId=self.__operation_id, data=keys, hostedAppId=C.APP_ID, secret=self.__secret)
            _async_run(send_delete_dag(operation.model_dump_json(), DELETE_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id))

        async def async_delete(self, keys: List[str]) -> None:
            if self.__is_local:
                raise Exception("object storage not allow in local mode yet")
            operation = KeysWithSynchronize(operationId=self.__operation_id, data=keys, hostedAppId=C.APP_ID, secret=self.__secret)
            await send_delete_dag(operation.model_dump_json(), DELETE_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id)

    """context for run"""
    def __init__(self, operation_id: str = None, run_id: str = None, app_id: str = None, app_cfg: Dict[str, Any] = None, msg_url: str = None, email: Optional[str] = None, dag_host_port: str = None, secret: str = None, single_pod: bool = None, indexes: int = None, index: Optional[int] = None, login: str = None, japp_logs_buffer: io.StringIO = None, local_storage: Optional['LocalStorage'] = None, logger_fun: Optional[Callable[[str, Optional[str], Optional[str], bool], logging.Logger]] = None, *, initialize: bool = True):
        if not initialize:  # need for types, use only copy with _fix_app_cfg
            return
        self.__operation_id = operation_id
        self.app_id = app_id
        self.run_id = run_id
        self.app_cfg: Union[MinimalCfg, Dict[str, Any]] = app_cfg
        self.msg_url = msg_url
        self.email = email
        self.dag_key_value = Context._DagKeyValue(operation_id, run_id, dag_host_port, secret, local_storage)
        self.object_storage = Context._ObjectStorage(operation_id, dag_host_port, secret, single_pod, local_storage)
        self.__secret = secret
        self.__single_pod = single_pod
        self.__metadata: Dict[str, Optional[str]] = {}
        self.__dag_host_port = dag_host_port
        self.__indexes = indexes
        self.__index = index or 0   # ok?
        self.__login = login
        self.common = None
        self.__japp_logs_buffer = japp_logs_buffer
        self.__is_local = local_storage is not None
        self.__local_storage = local_storage
        self.__pauses = {}

        if logger_fun is None:
            self.__logger_buf = io.StringIO()
            self.logger = self.__set_logger()
        else:
            self.__logger_buf = LocalLogsBuffer(logger_fun, operation_id, run_id, app_id, True)
            self.logger = self.__logger_buf.logger
            self.__set_logger(self.logger)

    def _fix_app_cfg(self, extra_context: Optional[Context] = None):
        if extra_context is None:
            extra_context = self
        if hasattr(extra_context, "__orig_class__"):
            try:
                self.app_cfg = _dict_with_class(extra_context)(self.app_cfg)
            except BaseException as ex:
                if C.STRICT_APP_CFG_TYPE:
                    raise ex
                self.__japp_logs_buffer.write(f"app cfg scheme parse err: {ex}\n")

    def __set_logger(self, logger: Optional[logging.Logger] = None):
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

        stream_handler = logging.StreamHandler(self.__logger_buf)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        if logger is None:
            logger = logging.getLogger(f"{self.operation_id}${self.run_id}")
            logger.setLevel(logging.INFO)
            logger.addHandler(stream_handler)

        uvicorn_logger = logging.getLogger("uvicorn")
        for handler in uvicorn_logger.handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _logs(self, clear: bool = True):
        data = self.__logger_buf.getvalue()
        if clear:
            self.__logger_buf.truncate(0)
            self.__logger_buf.seek(0)
        return data

    def _set_index(self, index: int):
        self.__index = index

    def __share(self, path: str, all_runs: bool, path_prefix: str, force: bool, ignore_not_exists: bool = False) -> bool:
        run_id = f"/{self.run_id}" if not all_runs else ""
        realpath = f"{path_prefix}/{path}"
        if not os.path.exists(realpath):
            assert ignore_not_exists, f"path not exist: {realpath}"
            return False
        mnt_path = f"{C.STORAGE_PATH(self.__operation_id)}{run_id}/{path}"
        if force and os.path.exists(mnt_path):
            self.delete_share(path=path, all_runs=all_runs)
        os.makedirs(os.path.dirname(mnt_path), exist_ok=True)
        if Path(realpath).is_file():
            shutil.copy(realpath, mnt_path)
        elif Path(realpath).is_dir():
            shutil.copytree(realpath, mnt_path)
        else:
            raise Exception(f"path is not file or directory: {realpath}")
        return True

    def __share_many(self, paths: List[str], all_runs: bool, path_prefix: str, force: bool) -> List[str]:
        shared_paths = []
        for path in paths:
            if self.__share(path, all_runs, path_prefix, force, ignore_not_exists=True):
                shared_paths.append(path)
        return shared_paths

    def share(self, path: str, all_runs: bool = False, path_prefix: str = APP_DIR, force: bool = False, synchronize: bool = True) -> None:
        """copy dir (if it doesn't already exist or \"force\"=True) or file along the path starting from the \"path_prefix\" (\"apps\" directory in app by default) to the shared directory for all apps"""
        self.__share(path, all_runs, path_prefix, force)
        if synchronize:
            self.synchronize(paths=[path], all_runs=all_runs)

    async def async_share(self, path: str, all_runs: bool = False, path_prefix: str = APP_DIR, force: bool = False, synchronize: bool = True) -> None:
        """copy dir (if it doesn't already exist or \"force\"=True) or file along the path starting from the \"path_prefix\" (\"apps\" directory in app by default) to the shared directory for all apps"""
        self.__share(path, all_runs, path_prefix, force)
        if synchronize:
            await self.async_synchronize(paths=[path], all_runs=all_runs)

    def share_many(self, paths: List[str], all_runs: bool = False, path_prefix: str = APP_DIR, force: bool = False, synchronize: bool = True) -> None:
        """same as share but for multiple paths, ignore not exists path"""
        paths = self.__share_many(paths, all_runs, path_prefix, force)
        if len(paths) == 0:
            return
        if synchronize:
            self.synchronize(paths=paths, all_runs=all_runs)

    async def async_share_many(self, paths: List[str], all_runs: bool = False, path_prefix: str = APP_DIR, force: bool = False, synchronize: bool = True) -> None:
        """same as share but for multiple paths, ignore not exists path"""
        paths = self.__share_many(paths, all_runs, path_prefix, force)
        if len(paths) == 0:
            return
        if synchronize:
            await self.async_synchronize(paths=paths, all_runs=all_runs)

    def get_share_path(self, path: str, all_runs: bool = False, not_exist_ok: bool = False) -> str:
        """return real path by path, that shared before with function \"share\""""
        run_id = f"/{self.run_id}" if not all_runs else ""
        mnt_path = f"{C.STORAGE_PATH(self.__operation_id)}{run_id}/{path}"
        assert not_exist_ok or os.path.exists(mnt_path), f"path not exist: {path}"
        return mnt_path

    def __delete_share(self, path: str, all_runs: bool):
        realpath = self.get_share_path(path, all_runs)
        if Path(realpath).is_file():
            os.remove(realpath)
        elif Path(realpath).is_dir():
            shutil.rmtree(realpath)
        else:
            raise Exception(f"path is not file or directory: {path}")

    def delete_share(self, path: str, all_runs: bool = False, synchronize: bool = True) -> None:
        """delete dir or file, that shared between all apps, path like path is the same as used in function \"share\""""
        if synchronize and not self.__single_pod:
            run_id = self.run_id if not all_runs else None
            operation = KeysWithSynchronize(operationId=self.__operation_id, data=[path], runId=run_id, hostedAppId=C.APP_ID, secret=self.__secret, local=True)
            _async_run(send_delete_dag(operation.model_dump_json(), DELETE_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id))
        else:
            self.__delete_share(path, all_runs)

    async def async_delete_share(self, path: str, all_runs: bool = False, synchronize: bool = True) -> None:
        """delete dir or file, that shared between all apps, path like path is the same as used in function \"share\""""
        if synchronize and not self.__single_pod:
            run_id = self.run_id if not all_runs else None
            operation = KeysWithSynchronize(operationId=self.__operation_id, data=[path], runId=run_id, hostedAppId=C.APP_ID, secret=self.__secret, local=True)
            await send_delete_dag(operation.model_dump_json(), DELETE_OBJ_STORAGE(self.__dag_host_port), operation_id=self.__operation_id)
        else:
            self.__delete_share(path, all_runs)

    def __objects_url(self, all_runs: bool):
        url = f"{OBJECTS(self.__dag_host_port)}/{C.APP_ID}/{self.__operation_id}"
        if not all_runs:
            url += f"/{self.run_id}"
        return url

    def synchronize(self, paths: Optional[List[str]] = None, all_runs: bool = False) -> None:
        """synchronize mounts for pods, paths = None or [] - synchronize from root mount"""
        if not self.__single_pod:
            paths = [] if paths is None else paths
            run_id = self.run_id if not all_runs else None
            if C.IS_EXTERNAL:
                data = zip_raw(paths, self.__operation_id, run_id, self.__japp_logs_buffer)
                if data is not None and len(data) > 0:
                    if C.WS is not None:
                        payload = base64.b64encode(data).decode('utf-8')
                        data = ObjectRequest(
                            operationId=self.__operation_id,
                            runId=None if all_runs else self.run_id,
                            hostedAppId=C.APP_ID,
                            payload=payload,
                        ).model_dump_json()
                        url = OBJECTS(self.__dag_host_port)
                    else:
                        url = self.__objects_url(all_runs)
                    _async_run(send_post_dag(data, url, headers={'Content-type': 'application/octet-stream'}, operation_id=self.__operation_id))    # TODO secret
            else:
                settings = SynchronizeSettings(operationId=self.__operation_id, runId=run_id, paths=paths, hostedAppId=C.APP_ID, secret=self.__secret)
                _async_run(send_post_dag(settings.model_dump_json(), SYNCHRONIZE(self.__dag_host_port), operation_id=self.__operation_id))

    async def async_synchronize(self, paths: Optional[List[str]] = None, all_runs: bool = False) -> None:
        """synchronize mounts for pods, paths = None or [] - synchronize from root mount"""
        if not self.__single_pod:
            paths = [] if paths is None else paths
            run_id = self.run_id if not all_runs else None
            if C.IS_EXTERNAL:
                data = zip_raw(paths, self.__operation_id, run_id, self.__japp_logs_buffer)
                if data is not None and len(data) > 0:
                    if C.WS is not None:
                        payload = base64.b64encode(data).decode('utf-8')
                        data = ObjectRequest(
                            operationId=self.__operation_id,
                            runId=None if all_runs else self.run_id,
                            hostedAppId=C.APP_ID,
                            payload=payload,
                        ).model_dump_json()
                        url = OBJECTS(self.__dag_host_port)
                    else:
                        url = self.__objects_url(all_runs)
                    await send_post_dag(data, url, headers={'Content-type': 'application/octet-stream'}, operation_id=self.__operation_id)   # TODO secret
            else:
                settings = SynchronizeSettings(operationId=self.__operation_id, runId=run_id, paths=paths, hostedAppId=C.APP_ID, secret=self.__secret)
                await send_post_dag(settings.model_dump_json(), SYNCHRONIZE(self.__dag_host_port), operation_id=self.__operation_id)

    async def __send_msg(self, data, url, headers, wrap, with_result):
        try:
            if not isinstance(data, str):
                data = json.dumps(data)
            if wrap:
                data = Info(data=data, operationId=self.__operation_id, infoType="msg").model_dump_json()
            if headers is None or wrap:
                headers = {'Content-type': 'application/json'}
            async with aiohttp.ClientSession(timeout=C.AIOHTTP_TIMEOUT) as session:
                async with session.post(url, data=data, headers=headers) as response:
                    response.raise_for_status()
                    res = await response.json()
                    if with_result:
                        log_info(f"msg to {url}, response returned", context_logger)
                        return res
                    else:
                        log_info(f"msg to {url} response: {res}", context_logger)
        except:
            log_error(f"msg to {url} failed", context_logger)
            log_error(traceback.format_exc(), context_logger)

    def msg(self, data: Union[str, Dict], url: Optional[str] = None, headers: Optional[Dict[str, str]] = None, wait: bool = False, wrap: bool = True, with_result: bool = False):
        """send http msg to system or any url

        Args:
            data (Union[str, Dict]): msg data
            url (Optional[str]): url to which the request is sent. If not specified, the default url is used (system url, but it can be overridden in the startup cfg, the parameter is msg_url). system url. Defaults to None.
            headers (Optional[Dict[str, str]]): Just headers, with which the request is sent. Defaults to None.
            wait (bool): wait result. Defaults to False.
            wrap (bool): need system wrap with operationId. Defaults to True.
            with_result (bool): return result. Defaults to False.
        """
        return _async_run(self.async_msg(data, url, headers, wait, wrap, with_result))

    async def async_msg(self, data: Union[str, Dict], url: Optional[str] = None, headers: Optional[Dict[str, str]] = None, wait: bool = False, wrap: bool = True, with_result: bool = False):
        """send http msg to system or any url

        Args:
           data (Union[str, Dict]): msg data
           url (Optional[str]): url to which the request is sent. If not specified, the default url is used (system url, but it can be overridden in the startup cfg, the parameter is msg_url). system url. Defaults to None.
           headers (Optional[Dict[str, str]]): Just headers, with which the request is sent. Defaults to None.
           wait (bool): wait result. Defaults to False.
           wrap (bool): need system wrap with operationId. Defaults to True.
           with_result (bool): return result. Defaults to False.
        """
        if url is None:
            url = self.msg_url
            assert url is not None, "one of {\"url\", \"run_id\"} should be not None"
        if wait:
            return await self.__send_msg(data, url, headers, wrap, with_result)
        else:
            send_background_task(self.__send_msg, data, url, headers, wrap, with_result, logs_buffer=self.__japp_logs_buffer)
            await asyncio.sleep(C.SLEEP_BACKGROUND_TASK_S)

    def email_send(self, message: str, subject: Optional[str] = None, type: str = "gmail") -> None:
        """only gmail work now, if subject is None used default"""
        if self.__is_local:
            raise Exception("email_send not allow in local mode yet")
        if self.email is None:
            log_warn("cfg email is None, email_send ignored", context_logger)
            return
        msg = Message(operationId=self.__operation_id, type=type, receivers=[self.email], subject=subject, message=message, hostedAppId=C.APP_ID, secret=self.__secret)
        try:
            _async_run(send_post_dag(msg.model_dump_json(), MESSAGE(self.__dag_host_port), raw_res=True, operation_id=self.__operation_id)) # FIXME
        except:
            log_warn("email_send failed", context_logger)

    def _set_metadata(self, metadata: Dict[str, Optional[str]]):
        self.__metadata.update(metadata)

    def metadata(self, df_name: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """get metadata by df_name"""
        cur_metadata = self.__metadata.get(df_name)
        if cur_metadata is not None:
            try:
                if isinstance(cur_metadata, str):
                    return json.loads(cur_metadata)
                else:
                    assert isinstance(cur_metadata, List), "wrong metadata type"
                    return [json.loads(cur_submetadata) for cur_submetadata in cur_metadata]
            except:
                log_error("wrong metadata", context_logger)
                log_error(traceback.format_exc(), context_logger)
        return None

    @property
    def scale_info(self) -> Tuple[int, int]:
        """return scale app number (in [0..scale)) and scale"""
        return self.__index, self.__indexes

    def get_scale_part(self, jdf: JDF) -> JDF:
        """return scale part of jdf"""
        if isinstance(jdf, DFS) or isinstance(jdf, Sink):
            return jdf._apply(self.get_scale_part)
        elif isinstance(jdf, Docs):
            div, mod = divmod(len(jdf), self.__indexes)
            return jdf[div * self.__index + min(mod, self.__index):div * (self.__index + 1) + min(mod, self.__index + 1)]
        elif isinstance(jdf, pd.DataFrame):
            div, mod = divmod(jdf.shape[0], self.__indexes)
            return DF(jdf.iloc[div * self.__index + min(mod, self.__index):div * (self.__index + 1) + min(mod, self.__index + 1)].copy())
        else:
            return jdf

    @property
    def operation_id(self) -> str:
        return self.__operation_id

    def has_object(self, path: str) -> bool:
        real_path = os.path.join(C.COLLECTIONS_OBJ_PATH(self.__login), path)
        return os.path.exists(real_path)

    def get_object(self, path: str) -> OBJ:
        real_path = os.path.join(C.COLLECTIONS_OBJ_PATH(self.__login), path)
        assert os.path.exists(real_path), f"not exist object by path={path}"
        return OBJ(real_path)

    @cached_property
    def object_prefix(self) -> str:
        return C.COLLECTIONS_OBJ_PATH(self.__login)

    def as_object(self, path_from: str, path_to: str, path_prefix: Optional[str] = None, *, dir: Optional[str] = None, move: bool = False, replace_strategy: bool = False, allow_update_dir: bool = True, ignore_not_exist: bool = False) -> Optional[OBJ]:
        """replace_strategy: replace if True, merge otherwise (on exist directory), None if ignore_not_exist=True and not success"""
        objs = self.as_objects({path_from: path_to}, path_prefix=path_prefix, dir=dir, move=move, replace_strategy=replace_strategy, allow_update_dir=allow_update_dir, ignore_not_exist=ignore_not_exist)
        return objs[0] if len(objs) > 0 else None

    def as_objects(self, paths: Dict[str, str], path_prefix: Optional[str] = None, *, dir: Optional[str] = None, move: bool = False, replace_strategy: bool = False, allow_update_dir: bool = True, ignore_not_exist: bool = False, return_dir: bool = False) -> Union[List[OBJ], OBJ]:
        """replace_strategy: replace if True, merge otherwise (on exist directory), if return_dir - return OBJ with prefix, else List[OBJ]"""
        if dir is None:
            dir = str(uuid4())
        prefix = os.path.join(C.COLLECTIONS_OBJ_PATH(self.__login), dir)
        assert allow_update_dir or not os.path.exists(prefix), f"rewriting along the path is prohibited (path={dir})"
        os.makedirs(prefix, exist_ok=allow_update_dir)

        objs = []
        for path_from, subpath_to in paths.items():
            if path_prefix is not None:
                path_from = os.path.join(path_prefix, path_from)
            path_to = os.path.join(prefix, subpath_to)
            os.makedirs(os.path.dirname(path_to), exist_ok=True)
            cur_path = Path(path_from)
            if cur_path.is_file():
                if move:
                    os.replace(path_from, path_to)
                else:
                    shutil.copy(path_from, path_to)
                objs.append(OBJ(path_to, is_new=True))
            elif cur_path.is_dir():
                if replace_strategy and os.path.exists(path_to):
                    shutil.rmtree(path_to)
                if move:
                    if not os.path.exists(path_to):
                        shutil.move(path_from, path_to)
                    else:
                        merge_move_dir(path_from, path_to)
                else:
                    shutil.copytree(path_from, path_to, dirs_exist_ok=True)
                objs.append(OBJ(path_to, is_new=True))
            else:   # not add to objs
                if not ignore_not_exist:
                    raise Exception(f"unknown path: {path_from}")
                self.__logger_buf.write(f"as_object warn: unknown path: {path_from}")
        if return_dir:
            return OBJ(prefix, is_new=True)
        else:
            return objs

    def _set_pauses(self, pauses: Dict[str, asyncio.Future]):
        self.__pauses = pauses

    @property
    def pause(self) -> Pause:
        return Pause(self.__pauses)


def to_binary(smth: Any) -> bytes:
    return pickle.dumps(smth)


def from_binary(smth: bytes) -> Any:
    return pickle.loads(smth)


def load(url: str, path: str, path_prefix: str = APP_DIR) -> None:
    """path - relative: starting from the \"path_prefix\" (\"apps\" directory in app by default)"""
    response = requests.get(url)
    response.raise_for_status()
    with open(f"{path_prefix}/{path}", 'wb') as f:
        f.write(response.content)


_Tensor = TypeVar('_Tensor', bound='torch.Tensor')
_kshort = 0b111  # last two-byte char encodes <= 7 bits
_kexclude_idx = {chr(0): 0, chr(10): 1, chr(
    13): 2, chr(34): 3, chr(38): 4, chr(92): 5}
_idx_exclude = {0: chr(0), 1: chr(10), 2: chr(
    13), 3: chr(34), 4: chr(38), 5: chr(92)}


def _base_encode(data: bytes) -> str:
    idx = (bit := 0)

    def get7(length):
        """get 7 bits from data"""
        nonlocal idx, bit, data
        if idx >= length:
            return False, 0

        # AND mask to get the first 7 bits
        f_ = (((0b11111110 % 0x100000000) >> bit) & data[idx]) << bit
        f_ = f_ >> 1
        bit += 7
        if bit < 8:
            return True, f_
        bit -= 8
        idx += 1
        if idx >= length:
            return True, f_
        secondPart = (((0xFF00 % 0x100000000) >> bit) & data[idx]) & 0xFF
        secondPart = secondPart >> (8 - bit)
        return True, f_ | secondPart

    _out = bytearray()
    while True:
        rbits, bits = get7(len(data))
        if not rbits:
            break
        if bits in _kexclude_idx:
            illegalIndex = _kexclude_idx[bits]
        else:
            _out.append(bits)
            continue
        retNext, nextBits = get7(len(data))
        b1 = 0b11000010
        b2 = 0b10000000
        if not retNext:
            b1 |= (0b111 & _kshort) << 2
            nextBits = bits
        else:
            b1 |= (0b111 & illegalIndex) << 2
        firstBit = 1 if (nextBits & 0b01000000) > 0 else 0
        b1 |= firstBit
        b2 |= nextBits & 0b00111111
        _out += [b1, b2]
    return ''.join([chr(x) for x in _out])


def _base_decode(encoded_data: str) -> bytes:
    encoded_data = [ord(x) for x in encoded_data]
    decoded = []
    curByte = bitOfByte = 0

    def push7(byte):
        nonlocal curByte, bitOfByte, decoded
        byte <<= 1
        curByte |= (byte % 0x100000000) >> bitOfByte
        bitOfByte += 7
        if bitOfByte >= 8:
            decoded += [curByte]
            bitOfByte -= 8
            curByte = (byte << (7 - bitOfByte)) & 255
        return

    for i in range(len(encoded_data)):
        if encoded_data[i] > 127:
            illegalIndex = ((encoded_data[i] % 0x100000000) >> 8) & 7
            if illegalIndex != _kshort:
                push7(_idx_exclude[illegalIndex])
            push7(encoded_data[i] & 127)
        else:
            push7(encoded_data[i])
    return bytearray(decoded)


def _tensor_to_df(x: List[_Tensor] | _Tensor) -> pd.DataFrame:
    import torch  # not in requirements
    import io

    if not isinstance(x, List):
        x = [x]

    shapes = []
    data = []
    grads = []
    device = []
    for x_ in x:
        assert isinstance(x_, torch.Tensor), f"not a tensor: {type(x_)}"
        # in-memory serialization using torch.save
        # to save autograd information and tensor type
        # https://pytorch.org/docs/stable/torch.html#torch.save
        buff = io.BytesIO()
        shape = x_.shape
        shapes.append(shape)
        device.append(x_.device)
        x_ = x_.cpu()
        torch.save(x_, buff)
        buff.seek(0)
        data.append(_base_encode(buff.read()))

        buff.close()
        buff = io.BytesIO()
        torch.save(x_.grad, buff)
        buff.seek(0)

        grads.append(_base_encode(buff.read()))

    return pd.DataFrame(
        {
            "__shape__": shapes,
            "__tensor__": data,
            "__grad__": grads,
            "__device__": device,
        })


def _tensor_from_df(x: pd.DataFrame) -> list:
    import torch  # not in requirements
    import io

    _out = []
    for _, row in x.iterrows():
        shape = row["__shape__"]
        encoded = row["__tensor__"]
        encoded_grad = row["__grad__"]
        decoded = _base_decode(encoded)
        decoded_grad = _base_decode(encoded_grad)
        buff = io.BytesIO(decoded)
        buff.seek(0)
        _t = torch.load(buff).reshape(shape)

        if _t.requires_grad:
            buff.close()

            buff = io.BytesIO(decoded_grad)
            buff.seek(0)
            _t.grad = torch.load(buff).reshape(shape)
            buff.close()

        if row["__device__"] != "cpu" and torch.cuda.is_available():
            _t = _t.to(row["__device__"])

        _out.append(_t)

    return _out


def to_df(x: Any, force: bool = False) -> pd.DataFrame:
    """creates a dataframe in a certain way, `force` should be used for complex objects ('ndarray', 'Tensor' and python primitives work without it. It crashes on basic types ('int', 'str', etc)), scheme of received dataframe - `default_scheme`"""  # noqa: E501
    if force:
        return pd.DataFrame({"data": [jsonpickle.encode(x)]})
    elif type(x).__name__ == "Tensor" or (isinstance(x, List) and len(x) > 0 and type(x[0]).__name__ == "Tensor"):
        return _tensor_to_df(x)
    elif isinstance(x, (np.ndarray, list, tuple, range, bytearray)):
        return pd.DataFrame({"data": x})
    elif isinstance(x, (set, frozenset)):
        return pd.DataFrame({"data": list(x)})
    elif isinstance(x, dict):
        return pd.DataFrame({"data": [json.dumps(x, default=pydantic_encoder)]})
    else:   # int, float, complex, str, bytes, bool
        return pd.DataFrame({"data": [x]})


# TODO create same with pyspark
def from_df(x: pd.DataFrame, type_name: Optional[str] = None, force: bool = False) -> Any:
    """decodes the `to_df` data from the dataframe, `force` is used if it was used in the encoding function - `to_df`. You should specify the type (by type_name: for example 'ndarray', 'list', 'Tensor', 'int') that was put in this `to_df` dataframe.
    possible type_names: 'ndarray', 'list', 'tuple', 'Tensor', 'set', 'frozenset', 'dict', 'bytearray'. Otherwise considered a primitive base type
    if force==True ignore type_name anyway"""  # noqa: E501
    if force:
        return jsonpickle.decode(x.data[0])
    elif type_name == 'ndarray':
        return x.data.values
    elif type_name == 'list':
        return x.data.values.tolist()
    elif type_name == 'tuple':
        return tuple(x.data.values.tolist())
    elif type_name == 'range':
        return x.data.values.tolist()
    elif type_name == 'Tensor' or ('__shape__' in x.columns and '__tensor__' in x.columns):
        # import torch  # not in requirements
        # return torch.from_numpy(x.values).float().to(torch.device('cpu'))   # can't work with gpu from inside yet  # noqa: E501
        return _tensor_from_df(x)
    elif type_name == 'set':
        return set(x.data.values.tolist())
    elif type_name == 'frozenset':
        return frozenset(x.data.values.tolist())
    elif type_name == 'dict':
        return json.loads(x.data[0])
    elif type_name == 'bytearray':
        return bytearray(x.data)
    else:   # int, float, complex, str, bytes, bool
        return x.data[0]


class MalevichException(Exception):
    pass
