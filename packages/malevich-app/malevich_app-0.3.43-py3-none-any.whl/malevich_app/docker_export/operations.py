import pandas as pd
import malevich_app.export.secondary.const as C
from copy import deepcopy
from typing import Optional, List, Tuple, Union, Dict, Any
from pydantic import BaseModel
from malevich_app.export.abstract.abstract import FixScheme, CollectionAndScheme
from malevich_app.export.jls.df import Doc, Docs
from malevich_app.export.jls.helpers import is_docs_scheme
from malevich_app.export.request.core_requests import post_request_json, get_mapping_schemes_raw, get_mapping_schemes
from malevich_app.export.secondary.EntityException import LOAD_COLLECTION_FAIL_MSG
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.endpoints import MONGO_LOAD
from malevich_app.export.secondary.helpers import get_collection_pandas, df_columns, obj_df, get_collection_json


async def get_df(julius_app, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]], Collection]:
    if julius_app.is_local:
        new_id = julius_app._local_storage.get_data(julius_app.operation_id, id, None if fix_scheme is None else fix_scheme.schemeName)
        res = {"result": "" if new_id is None else new_id}
    else:
        collection_and_scheme = CollectionAndScheme(operationId=julius_app.operation_id, collectionId=id, hostedAppId=C.APP_ID, secret=julius_app.secret, fixScheme=fix_scheme)
        res = await post_request_json(MONGO_LOAD(julius_app.dag_host_port), collection_and_scheme.model_dump_json(), buffer=julius_app.logs_buffer, fail_info=LOAD_COLLECTION_FAIL_MSG, operation_id=julius_app.operation_id)
    if id.startswith(JsonCollection.prefix) or (fix_scheme is not None and is_docs_scheme(fix_scheme.schemeName)):
        df_or_doc, _, metadata = get_collection_json(id, julius_app.operation_id)
    else:
        if res["result"] != "":     # update collection     # TODO not update id, ok?
            id = res["result"]
        df_or_doc, _, metadata = get_collection_pandas(id, julius_app.operation_id)
    collection = save_df_local(julius_app, df_or_doc, None if fix_scheme is None else fix_scheme.schemeName)
    julius_app.metadata[collection.get()] = metadata
    return df_or_doc, collection


async def get_doc_data(julius_app, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[Union[Dict, BaseModel], Collection]:
    if julius_app.is_local:
        julius_app._local_storage.get_data(julius_app.operation_id, id, None if fix_scheme is None else fix_scheme.schemeName)
    else:
        # FIXME do it inside - mapping like get_df_share
        collection_and_scheme = CollectionAndScheme(operationId=julius_app.operation_id, collectionId=id, hostedAppId=C.APP_ID, secret=julius_app.secret, fixScheme=fix_scheme)
        await post_request_json(MONGO_LOAD(julius_app.dag_host_port), collection_and_scheme.model_dump_json(), buffer=julius_app.logs_buffer, fail_info=LOAD_COLLECTION_FAIL_MSG, operation_id=julius_app.operation_id)
    data, scheme, metadata = get_collection_json(id, julius_app.operation_id)
    # ...
    collection = save_df_local(julius_app, data, None if fix_scheme is None else fix_scheme.schemeName)
    julius_app.metadata[collection.get()] = metadata
    return data, collection


def filter_collection_with_ids(julius_app, id: int, docs_ids: List[str]) -> Collection:
    julius_app.local_dfs.filter(id, docs_ids)
    return LocalCollection(id)


async def __get_df_with_update(julius_app, df: pd.DataFrame, scheme_name: str, scheme_name_to: str) -> pd.DataFrame:
    mapping = None
    if scheme_name is None:
        columns = df_columns(df)
        if scheme_name_to == "obj" and columns == ["path"]:
            mapping = {"path": "path"}
        else:
            if julius_app.is_local:
                mapping = julius_app._local_storage.get_mapping_schemes_raw(columns, scheme_name_to)
            else:
                mapping = await get_mapping_schemes_raw(columns, scheme_name_to, julius_app.operation_id, debug_mode=julius_app.debug_mode, buffer=julius_app.logs_buffer)
    elif scheme_name != scheme_name_to:
        if julius_app.is_local:
            mapping = julius_app._local_storage.get_mapping_schemes(scheme_name, scheme_name_to)
        else:
            mapping = await get_mapping_schemes(scheme_name, scheme_name_to, julius_app.operation_id, debug_mode=julius_app.debug_mode, buffer=julius_app.logs_buffer)

    df = df.rename(columns=dict(zip(df.columns, map(str, df.columns))))
    if mapping is not None:
        default_columns = []
        for column in ["__name__", "__id__"]:
            if column in df.columns:
                default_columns.append(column)
        df = df[list(mapping.keys()) + default_columns].rename(columns=mapping)
    return df


async def get_df_object_record(julius_app, id: str) -> Tuple[pd.DataFrame, Collection]:
    df = obj_df(julius_app, id)
    collection = save_df_local(julius_app, df, None)
    return df, collection


async def get_df_local(julius_app, id: int, scheme_name_to: Optional[str]) -> Tuple[Union[pd.DataFrame, Dict, List, BaseModel], Collection]:
    df, scheme_name = julius_app.local_dfs.get(id)
    assert df is not None, f"internal error: get_df_local ({id})"
    if isinstance(df, Dict) or isinstance(df, List) or issubclass(df.__class__, BaseModel):
        return deepcopy(df), LocalCollection(id, is_doc=True)   # FIXME optimize copy
    if scheme_name_to is None or julius_app.is_internal_scheme(scheme_name_to):  # no new scheme or JsonCollection
        return df.copy(), LocalCollection(id)                   # FIXME optimize copy
    return await __get_df_with_update(julius_app, df, scheme_name, scheme_name_to), LocalCollection(id)


async def get_df_share(julius_app, id: str, scheme_name_to: Optional[str]) -> Tuple[pd.DataFrame, Collection]:
    df, scheme, metadata = get_collection_pandas(id, julius_app.operation_id)   # FIXME or json?
    scheme_name = scheme.get("schemeName") if scheme is not None else None
    if not id.startswith(JsonCollection.prefix) and scheme_name_to is not None and not is_docs_scheme(scheme_name_to) and not julius_app.is_internal_scheme(scheme_name_to):
        df = await __get_df_with_update(julius_app, df, scheme_name, scheme_name_to)
    collection = save_df_local(julius_app, df, scheme_name_to)
    julius_app.metadata[collection.get()] = metadata
    return df, collection


def save_df_local(julius_app, df_or_doc: Union[pd.DataFrame, Doc, BaseModel, Dict, List, Docs], scheme_name: Optional[str] = None) -> Collection:
    if isinstance(df_or_doc, Doc) or isinstance(df_or_doc, Docs):
        df_or_doc = df_or_doc.parse()
    id = julius_app.local_dfs.post(df_or_doc, scheme_name)
    return LocalCollection(id, is_doc=isinstance(df_or_doc, Dict) or isinstance(df_or_doc, List) or issubclass(df_or_doc.__class__, BaseModel))
