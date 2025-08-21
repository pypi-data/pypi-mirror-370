import json
import aiohttp
from io import StringIO
from typing import Optional, Dict, Union, Any, List
from pydantic.v1.json import pydantic_encoder
from malevich_app.export.abstract.abstract import FixScheme, SchemesMappingNames, SchemesMappingRaw, DocsCollectionRun, \
    CollectionCopy, FailStructure
from malevich_app.export.request.dag_requests import _ws
from malevich_app.export.secondary.LogHelper import log_error
import malevich_app.export.secondary.const as C
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.export.secondary.collection.MongoCollection import MongoCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
import malevich_app.export.secondary.endpoints as end

from malevich_app.export.secondary.helpers import get_collection_pandas, obj_df, get_collection_json, \
    exist_collection_pandas

_mongo_load_ws = end.MONGO_LOAD("")


async def post_request_json(path: str, data: str, text: bool = False, buffer: Optional[StringIO] = None, fail_info: Optional[str] = None, operation_id: Optional[str] = None) -> Optional[Union[str, Dict[str, Any]]]:
    if path == _mongo_load_ws:
        return await _ws(operation_id, path, data)
    else:
        async with aiohttp.ClientSession(timeout=C.AIOHTTP_TIMEOUT) as session:
            async with session.post(path, data=data, headers=C.DEFAULT_HEADERS) as response:
                if response.status == 204:
                    return None
                if not response.ok:
                    res = await response.text()
                    try:
                        res = json.loads(res)["result"]
                    except:
                        pass
                    msg_prefix = fail_info if fail_info is not None else "post request failed"
                    log_error(f"error: {msg_prefix}: {res}")
                    if buffer is None:
                        print(f"error: {msg_prefix}: {res}")
                    else:
                        buffer.write(f"error: {msg_prefix}: {res}\n")
                if not response.ok:
                    raise EntityException(fail_info)
                res = await response.text() if text else await response.json()
                return res


async def save_real_collection(collection: Collection, julius_app, name: Optional[str], index: int, *, group_name: Optional[str] = None, save_force: bool = False) -> Collection:
    if isinstance(collection, MongoCollection) and not save_force and not exist_collection_pandas(collection.get(), julius_app.operation_id):
        collection_copy = CollectionCopy(operationId=julius_app.operation_id, runId=julius_app.run_id, collectionId=collection.get(), name=name or "coll", groupName=group_name, index=index)
        collection_id = await post_request_json(end.COPY_COLLECTION, collection_copy.model_dump_json(), text=True, buffer=julius_app.logs_buffer)
        return MongoCollection(collection_id)

    is_doc = False
    if isinstance(collection, ObjectCollection):
        docs, scheme = obj_df(julius_app, collection.get(), with_prefix=False), None    # "obj" scheme
        if not julius_app.is_local:
            data = list(map(lambda row: row[1].drop(["__id__", "__name__"], errors="ignore").to_json(), docs.iterrows()))
    else:
        is_doc = isinstance(collection, JsonCollection)
        if is_doc:
            coll_id = collection.get(with_prefix=True)
            docs, scheme, _ = get_collection_json(coll_id, julius_app.operation_id)
            if not julius_app.is_local:
                if isinstance(docs, List):
                    data = [json.dumps(doc, default=pydantic_encoder) for doc in docs]
                else:
                    data = [json.dumps(docs, default=pydantic_encoder)]
        else:
            coll_id = collection.get()
            docs, scheme, _ = get_collection_pandas(coll_id, julius_app.operation_id)
            if not julius_app.is_local:
                data = list(map(lambda row: row[1].drop(["__id__", "__name__"], errors="ignore").to_json(), docs.iterrows()))

    if julius_app.is_local:
        collection_id = julius_app._local_storage.save_data(julius_app.operation_id, julius_app.run_id, docs, scheme, name or "coll", group_name, index, is_doc)
    else:
        collection_run = DocsCollectionRun(operationId=julius_app.operation_id, runId=julius_app.run_id,
                                           data=data, fixScheme=None if scheme is None else FixScheme(schemeName=scheme["schemeName"], mode=scheme["mode"]),
                                           name=name or "coll", groupName=group_name, index=index, isDoc=is_doc)
        collection_id = await post_request_json(end.DOCS_COLLECTION, collection_run.model_dump_json(), text=True, buffer=julius_app.logs_buffer)     # save real collection
    if name is not None:    # save for continue pipline (save data from output)
        julius_app.logs_buffer.write(f"info: save collection: {name}\n")
    return MongoCollection(collection_id, base=collection)


async def get_mapping_schemes(scheme_name_from: str, scheme_name_to: str, operation_id: str, buffer: StringIO, debug_mode: bool=False) -> Dict[str, str]:
    schemes_mapping_names = SchemesMappingNames(operationId=operation_id, schemeFromName=scheme_name_from, schemeToName=scheme_name_to)
    mapping = await post_request_json(end.MAPPING_SCHEMES_NAMES, schemes_mapping_names.model_dump_json(), buffer=buffer, fail_info=f"schemes mapping, {scheme_name_from} -> {scheme_name_to}")
    if debug_mode:
        buffer.write(f"info: mapping: {mapping['data']}\n")
    return mapping["data"]


async def get_mapping_schemes_raw(columns: List[str], scheme_name_to: str, operation_id: Optional[str] = None, buffer: Optional[StringIO] = None, debug_mode: bool=False) -> Dict[str, str]:
    schemes_mapping_raw = SchemesMappingRaw(operationId=operation_id, columns=columns, schemeToName=scheme_name_to)
    mapping = await post_request_json(end.MAPPING_SCHEMES_RAW, schemes_mapping_raw.model_dump_json(), buffer=buffer, fail_info=f"schemes mapping raw, {columns} -> {scheme_name_to}")
    if debug_mode:
        if buffer is None:
            print(f"info: mapping: {mapping['data']}")
        else:
            buffer.write(f"info: mapping: {mapping['data']}\n")
    return mapping["data"]


async def post_error_info(data: FailStructure, buffer: StringIO):
    await post_request_json(end.ERROR_INFO, data.model_dump_json(), text=True, buffer=buffer, fail_info=f"post error info")
