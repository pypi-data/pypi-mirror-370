import asyncio
import base64
import io
import json
import os
import random as rand
import shutil
import string
import traceback
from asyncio import Future
from enum import Enum
from logging import Logger
from uuid import uuid4
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
import pandas as pd
from pydantic import BaseModel
from pydantic.v1.json import pydantic_encoder
from starlette.concurrency import run_in_threadpool
from malevich_app.export.abstract.abstract import Collection as Coll, Objects, FixScheme, CollectionsRequest, \
    ObjectRequest
from malevich_app.export.jls.df import OBJ, DF, Doc, Docs
from malevich_app.export.jls.helpers import is_async
from malevich_app.export.request.dag_requests import send_post_dag
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.LogHelper import log_warn, log_error
import malevich_app.export.secondary.const as C
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.export.secondary.collection.MongoCollection import MongoCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.collection.ShareCollection import ShareCollection
from malevich_app.export.secondary.endpoints import OBJECTS, COLLECTIONS
from malevich_app.export.secondary.zip import zip_raw, zip_raw_collections

background_tasks = set()
__parquet_prefix = "PARGO_PREFIX_"


class ContextPosition(Enum):
    START = "start"
    END = "end"
    NONE = "none"


def reverse_dict(m: Dict):
    return {v: k for k, v in m.items()}


def rand_str(size: int = 10, chars=string.ascii_letters):
    return ''.join(rand.choice(chars) for _ in range(size))


def get_db_type_by_url(url: str):   # TODO(fix it)
    if url.startswith("jdbc:mysql"):
        return "MySQL"
    if url.startswith("jdbc:postgresql"):
        return "MySQL"
    log_warn("unable to understand database type")
    return "AnyJDBCSQL"


def flat_docs(row: Dict[str, str]):
    return {**json.loads(row['data']), "__name__": row["name"], "__id__": row["id"]}


def fix_df_id_name(df: pd.DataFrame):
    if "__name__" not in df:
        df["__name__"] = df.apply(lambda _: "", axis=1)
    if "__id__" not in df:
        df["__id__"] = df.apply(lambda _: str(uuid4()), axis=1)


def send_background_task(fun: callable, *args, logs_buffer: Optional[io.StringIO] = None, ignore_errors: bool = False, new_loop: bool = False, **kwargs) -> Future:
    if is_async(fun):
        call = fun(*args, **kwargs)
        if new_loop:
            call = run_in_threadpool(asyncio.run, call)
    else:
        call = run_in_threadpool(fun, *args, **kwargs)

    future = asyncio.ensure_future(call)
    background_tasks.add(future)

    def _cleanup_future(future: Future[None]):
        background_tasks.discard(future)
        if not ignore_errors and (ex := future.exception()):
            if logs_buffer is not None:
                logs_buffer.write(f"send_background_task error: {ex}\n")
            else:
                log_error(f"send_background_task error: {ex}")

    future.add_done_callback(_cleanup_future)
    return future


async def call_async_fun(fun: callable, logger: Logger, debug_mode: bool, buffer: Optional[io.StringIO], *, on_error=(False, [], {})) -> Union[Tuple[bool, List[Optional[Any]], Dict[str, Any]], Any]:
    try:
        res_schemes_names = await fun()
    except BaseException as ex:     # FIXME not ignore error type
        if buffer is not None:
            if debug_mode:
                buffer.write(f"error: {traceback.format_exc()}\n")
            else:
                buffer.write(f"error: {ex}\n")
        log_error(ex, logger)
        if isinstance(on_error, Callable):
            res_schemes_names = on_error(ex)
        else:
            res_schemes_names = on_error
    return res_schemes_names


def get_schemes_names(smth: List[Optional[Tuple[Optional[str], ...]]]) -> List[str]:
    schemes = set()
    for scheme in smth:
        if scheme is not None:
            for subscheme in scheme:
                if subscheme is not None:
                    if isinstance(subscheme, str):
                        schemes.add(subscheme)
                    else:
                        log_error(f"get_schemes_names: wrong subscheme {subscheme}")
    return list(schemes)


def save_collection(df: pd.DataFrame, operation_id: str, fix_scheme: Optional[FixScheme] = None) -> Collection:
    df = df.drop(["__id__", "__name__"], errors="ignore")
    df["__name__"] = df.apply(lambda _: "", axis=1)
    df["__id__"] = df.apply(lambda _: str(uuid4()), axis=1)
    collection_id = save_collection_pandas(df, operation_id, None if fix_scheme is None else fix_scheme.model_dump())
    return ShareCollection(collection_id)


def save_collection_pandas(df: pd.DataFrame, operation_id: str, scheme: Optional[Dict[str, Any]], *, coll_id: Optional[str] = None, path_by_operation_id: Optional[Callable[[str], str]] = None, save_format: Optional[str] = None) -> str:
    coll_id = str(uuid4()) if coll_id is None else coll_id
    if path_by_operation_id is None:
        path_by_operation_id = C.COLLECTIONS_PATH
    path = f"{path_by_operation_id(operation_id)}/{coll_id}"
    os.makedirs(path, exist_ok=True)    # mb override
    save_df(df, f"{path}/data", save_format=save_format)
    if scheme is not None:
        with open(f"{path}/scheme.json", 'w') as f:
            json.dump(scheme, f)
    return coll_id


def save_metadata(metadata: str, operation_id: str, coll_id: str):  # path should exist
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    with open(f"{path}/metadata.json", 'w') as f:
        f.write(metadata)


def save_collection_external(collection: Coll):
    if collection.isDoc:
        save_collection_json(collection.data, collection.operationId, None if collection.scheme is None else collection.scheme.model_dump(), coll_id=collection.id)
    else:
        df = pd.read_json(io.StringIO(collection.data))  # FIXME not only pandas
        fix_df_id_name(df)
        save_collection_pandas(df, collection.operationId, None if collection.scheme is None else collection.scheme.model_dump(), coll_id=collection.id)
    if collection.metadata is not None:
        save_metadata(collection.metadata, collection.operationId, collection.id)
    if collection.mapping is not None:
        with open(f"{C.COLLECTIONS_PATH(collection.operationId)}/{collection.id}/data-mapping.json", 'w') as f:
            json.dump(collection.mapping, f)


def get_collection_pandas(coll_id: str, operation_id) -> Tuple[pd.DataFrame, Optional[Dict[str, Any]], Optional[str]]:
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    if not (os.path.isfile(f"{path}/data") or (C.SAVE_DF_FORMAT != "csv" and os.path.isfile(f"{path}/data.csv"))):
        if os.path.exists(path):
            print(f"get_collection_pandas {path} ls: {os.listdir(path)}")                   # TODO temp, remove later
        else:
            colls_path = C.COLLECTIONS_PATH(operation_id)
            if os.path.exists(colls_path):
                print(f"get_collection_pandas {colls_path} ls: {os.listdir(colls_path)}")   # TODO temp, remove later
            else:
                print(f"get_collection_pandas {colls_path} not exist")                      # TODO temp, remove later
        if not os.path.isfile(f"{path}/data") and (C.SAVE_DF_FORMAT == "csv" or not os.path.isfile(f"{path}/data.csv")):
            raise EntityException("internal error: local collection not exist")
    if os.path.isfile(f"{path}/scheme.json"):
        with open(f"{path}/scheme.json", 'r') as f:
            scheme = json.load(f)
    else:
        scheme = None
    if os.path.isfile(f"{path}/metadata.json"):
        with open(f"{path}/metadata.json", 'r') as f:
            metadata = json.load(f)
    else:
        metadata = None
    return read_df(f"{path}/data"), scheme, metadata


def exist_collection_pandas(coll_id: str, operation_id) -> bool:
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    return os.path.isfile(f"{path}/data") or (C.SAVE_DF_FORMAT != "csv" and os.path.isfile(f"{path}/data.csv"))


def get_collection_json(coll_id: str, operation_id) -> Tuple[Union[Dict, List], Optional[Union[Dict[str, Any], List[Dict[str, Any]]]], Optional[str]]:
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    if not os.path.isfile(f"{path}/json"):
        raise EntityException("internal error: local json collection not exist")
    if os.path.isfile(f"{path}/scheme.json"):
        with open(f"{path}/scheme.json", 'r') as f:
            scheme = json.load(f)
    else:
        scheme = None
    if os.path.isfile(f"{path}/metadata.json"):
        with open(f"{path}/metadata.json", 'r') as f:
            metadata = json.load(f)
    else:
        metadata = None
    with open(f"{path}/json", 'r') as f:
        data = json.load(f)
    return data, scheme, metadata


def coll_obj_path(julius_app, id: str) -> str:
    path = os.path.join(C.COLLECTIONS_OBJ_PATH(julius_app._login), id)
    if not os.path.exists(path):
        raise EntityException(f"object collection with id=\"{id}\" not exist")
    return path


def obj_df(julius_app, path: str, *, with_prefix: bool = True, module=pd, **kwargs) -> DF['obj']:     # same in df.OBJ
    obj_path = coll_obj_path(julius_app, path)
    paths = []
    if os.path.isfile(obj_path):
        if with_prefix:
            paths.append(obj_path)
        else:
            paths.append(path)
    else:
        remove_prefix = None if with_prefix else f"{C.COLLECTIONS_OBJ_PATH(julius_app._login)}{os.sep}"
        for address, _, files in os.walk(obj_path):
            prefix = address if remove_prefix is None else address.removeprefix(remove_prefix)
            for name in files:
                paths.append(os.path.join(prefix, name))
    return DF['obj'](module.DataFrame.from_dict({"path": paths}, **kwargs))


async def get_df_object(julius_app, id: str, *, is_new: bool = False) -> Tuple[str, Collection]:
    path = coll_obj_path(julius_app, id)
    return path, ObjectCollection(id, with_prefix=False, is_new=is_new)


def df_columns(df: pd.DataFrame) -> List[str]:
    columns = []
    for column in df.columns:
        if column != "__name__" and column != "__id__":
            columns.append(column)
    return columns


def save_object_collection(julius_app, obj: OBJ) -> Collection:
    return ObjectCollection(obj.path.removeprefix(f"{C.COLLECTIONS_OBJ_PATH(julius_app._login)}{os.sep}"), with_prefix=False, is_new=obj._is_new)


def save_doc(doc: Union[Doc, Docs], operation_id: str, fix_scheme: Optional[FixScheme]) -> Collection:
    collection_id = save_collection_json(doc.json(), operation_id, None if fix_scheme is None else fix_scheme.model_dump())
    return JsonCollection(collection_id)


def save_collection_json(data: str, operation_id: str, scheme: Optional[Dict[str, Any]], *, coll_id: Optional[str] = None, path_by_operation_id: Optional[Callable[[str], str]] = None) -> str:
    coll_id = JsonCollection.prefix + str(uuid4()) if coll_id is None else coll_id
    if path_by_operation_id is None:
        path_by_operation_id = C.COLLECTIONS_PATH
    path = f"{path_by_operation_id(operation_id)}/{coll_id}"
    os.makedirs(path, exist_ok=True)    # mb override
    with open(f"{path}/json", 'w') as f:
        f.write(data)
    if scheme is not None:
        with open(f"{path}/scheme.json", 'w') as f:
            json.dump(scheme, f)
    return coll_id


def save_df(df: pd.DataFrame, path: str, *args, save_format: Optional[str] = None, **kwargs):
    if save_format is None:
        save_format = C.SAVE_DF_FORMAT
    if save_format == "csv":
        df.to_csv(path, index=False, *args, **kwargs)
    elif save_format == "parquet":
        df.to_parquet(path, index=False, *args, **kwargs)
    elif save_format == "feather":
        df.to_feather(path, *args, **kwargs)
    elif save_format == "pickle":
        df.to_pickle(path, *args, **kwargs)
    else:
        raise Exception(f"wrong SAVE_DF_FORMAT: {save_format}")


def read_df(path: str, pkg=pd, *args, **kwargs) -> pd.DataFrame:
    if C.SAVE_DF_FORMAT == "csv":
        try:
            df = pkg.read_csv(path, *args, **kwargs)
        except pkg.errors.EmptyDataError:    # FIXME handel other errors
            df = pkg.DataFrame()
        return df
    elif not os.path.exists(path) and os.path.exists(f"{path}.csv"):
        try:
            df = pkg.read_csv(f"{path}.csv", *args, **kwargs)
        except pkg.errors.EmptyDataError:    # FIXME handel other errors
            df = pkg.DataFrame()
        return df
    elif C.SAVE_DF_FORMAT == "parquet":
        df = pkg.read_parquet(path, *args, **kwargs)    # handle empty file errors
        mapping_path = f"{path}-mapping.json"
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r') as f:
                mapping = json.load(f)
                mapping["__name__"] = "__name__"
                mapping["__id__"] = "__id__"
            fixed_mapping = {}
            for column in df.columns:
                column_without_prefix = column.removeprefix(__parquet_prefix)
                column_to = mapping.get(column_without_prefix)
                if column_to is not None:
                    fixed_mapping[column] = column_to
            if len(mapping) != len(fixed_mapping):  # FIXME remove
                print(f"parquet, fix mapping failed: {mapping} -> {fixed_mapping}")
        else:
            fixed_mapping = {x: x.removeprefix(__parquet_prefix) for x in df.columns}
        df = df[list(fixed_mapping.keys())].rename(columns=fixed_mapping)
        return df
    elif C.SAVE_DF_FORMAT == "feather":
        return pkg.read_feather(path, *args, **kwargs)
    elif C.SAVE_DF_FORMAT == "pickle":
        return pkg.read_pickle(path, *args, **kwargs)
    else:
        raise Exception(f"wrong SAVE_DF_FORMAT: {C.SAVE_DF_FORMAT}")


async def reverse_object_request(objects: Objects, dag_host_port: str, logs_buffer: io.StringIO) -> bool:
    data = zip_raw(objects.paths, objects.operationId, objects.runId, logs_buffer, ignore_not_exist=True)
    if data is None:
        return False
    if len(data) == 0:
        return True

    url = f"{OBJECTS(dag_host_port)}/{C.APP_ID}/{objects.operationId}"
    if objects.runId is not None:
        url += f"/{objects.runId}"
    try:
        if C.WS is not None:
            payload = base64.b64encode(data).decode('utf-8')
            data = ObjectRequest(
                operationId=objects.operationId,
                runId=objects.runId,
                hostedAppId=C.APP_ID,
                payload=payload,
            ).model_dump_json()
            url = OBJECTS(dag_host_port)
        await send_post_dag(data, url, headers={'Content-type': 'application/octet-stream'}, operation_id=objects.operationId)    # TODO secret
    except:
        logs_buffer.write(f"{traceback.format_exc()}\n")
        return False
    return True


async def save_collections(julius_app, collections: List[Collection]):   # not for base apps
    main_collections = []
    new_obj_collections = []
    for collection in collections:
        if isinstance(collection, ObjectCollection):
            if collection._is_new:
                new_obj_collections.append(collection.get())
        else:
            main_collections.append(collection.get())

    tasks = []
    if len(main_collections) > 0:
        data = zip_raw_collections(main_collections, julius_app.operation_id, logs_buffer=julius_app.logs_buffer, asset=False)
        if data is not None and len(data) > 0:
            if C.WS is not None:
                payload = base64.b64encode(data).decode('utf-8')
                data = CollectionsRequest(
                    operationId=julius_app.operation_id,
                    asset=False,
                    hostedAppId=C.APP_ID,
                    payload=payload,
                )
                url = COLLECTIONS(julius_app.dag_host_port)
            else:
                url = f"{COLLECTIONS(julius_app.dag_host_port)}/{C.APP_ID}/{julius_app.operation_id}/false"
            tasks.append(send_post_dag(data, url, headers={'Content-type': 'application/octet-stream'}, operation_id=julius_app.operation_id))
    if len(new_obj_collections) > 0:
        data = zip_raw_collections(new_obj_collections, julius_app.operation_id, logs_buffer=julius_app.logs_buffer, asset=True, login=julius_app._login)
        if data is not None and len(data) > 0:
            if C.WS is not None:
                payload = base64.b64encode(data).decode('utf-8')
                data = CollectionsRequest(
                    operationId=julius_app.operation_id,
                    asset=True,
                    hostedAppId=C.APP_ID,
                    payload=payload,
                )
                url = COLLECTIONS(julius_app.dag_host_port)
            else:
                url = f"{COLLECTIONS(julius_app.dag_host_port)}/{C.APP_ID}/{julius_app.operation_id}/true"
            tasks.append(send_post_dag(data, url, headers={'Content-type': 'application/octet-stream'}, operation_id=julius_app.operation_id))
    if len(tasks) > 0:
        await asyncio.gather(*tasks)


def get_collection_by_id(collection_id: str) -> Collection:
    if collection_id.startswith(ObjectCollection.prefix):
        return ObjectCollection(collection_id)
    else:
        return MongoCollection(collection_id)


def json_schema(cl: BaseModel) -> str:
    res = cl.model_json_schema()
    if "properties" in res:
        for v in res["properties"].values():
            for variant in v.get("anyOf", []):
                if variant.get("type") == "null":
                    v["optional"] = True
    return json.dumps(res, default=pydantic_encoder)


def merge_move_dir(src: str, dst: str):
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            if os.path.isdir(dst_path):
                merge_move_dir(src_path, dst_path)
            else:
                shutil.move(src_path, dst_path)
        else:
            if os.path.exists(dst_path):
                os.replace(src_path, dst_path)
            else:
                shutil.move(src_path, dst_path)
    if not os.listdir(src):     # for updating the directory during the transfer process
        os.rmdir(src)


class DocsRaw:  # simple wrapper to type recognition
    def __init__(self, data: List[Dict[str, Any]]):
        self.__data = data

    def get(self) -> List[Dict[str, Any]]:
        return self.__data


class VariantList:  # simple wrapper to type recognition
    def __init__(self, data: List[Any]):
        self.__data = data

    def get(self) -> List[Any]:
        return self.__data
