import io
from typing import Optional, List, Tuple
from uuid import uuid4
import dask.dataframe as dd
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import FixScheme, CollectionAndScheme
from malevich_app.export.request.core_requests import post_request_json, get_mapping_schemes_raw, get_mapping_schemes
from malevich_app.export.secondary.EntityException import LOAD_COLLECTION_FAIL_MSG
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.collection.ShareCollection import ShareCollection
from malevich_app.export.secondary.endpoints import MONGO_LOAD
from malevich_app.export.secondary.helpers import df_columns, obj_df
from .helpers import get_collection_dask, save_collection_dask


async def get_df(julius_app, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[dd.DataFrame, Collection]:
    collection_and_scheme = CollectionAndScheme(operationId=julius_app.operation_id, collectionId=id, hostedAppId=C.APP_ID, secret=julius_app.secret, fixScheme=fix_scheme)
    res = await post_request_json(MONGO_LOAD(julius_app.dag_host_port), collection_and_scheme.model_dump_json(), buffer=julius_app.logs_buffer, fail_info=LOAD_COLLECTION_FAIL_MSG, operation_id=julius_app.operation_id)
    if res["result"] != "":     # update collection
        id = res["result"]
    df, _, metadata = get_collection_dask(id, julius_app.operation_id)
    collection = save_df_local(julius_app, df, None if fix_scheme is None else fix_scheme.schemeName)
    julius_app.metadata[collection.get()] = metadata
    return df, collection


def filter_collection_with_ids(julius_app, id: int, docs_ids: List[str]) -> Collection:
    julius_app.local_dfs.filter(id, docs_ids)
    return LocalCollection(id)


async def __get_df_with_update(df: dd.DataFrame, scheme_name: str, scheme_name_to: str, debug_mode: bool, operation_id: str, buffer: io.StringIO) -> dd.DataFrame:
    mapping = None
    if scheme_name is None:
        columns = df_columns(df)
        if scheme_name_to == "obj" and columns == ["path"]:
            mapping = {"path": "path"}
        else:
            mapping = await get_mapping_schemes_raw(columns, scheme_name_to, operation_id, debug_mode=debug_mode, buffer=buffer)
    elif scheme_name != scheme_name_to:
        mapping = await get_mapping_schemes(scheme_name, scheme_name_to, operation_id, debug_mode=debug_mode, buffer=buffer)

    df = df.rename(columns=dict(zip(df.columns, map(str, df.columns))))
    default_columns = []
    for column in ["__name__", "__id__"]:
        if column in df.columns:
            default_columns.append(column)
    if mapping is not None:
        df = df[list(mapping.keys()) + default_columns].rename(columns=mapping)
    return df


async def get_df_object_record(julius_app, id: str) -> Tuple[dd.DataFrame, Collection]:
    df = obj_df(julius_app, id, module=dd, npartitions=1)
    collection = save_df_local(julius_app, df, None)
    return df, collection


async def get_df_local(julius_app, id: int, scheme_name_to: Optional[str]) -> Tuple[dd.DataFrame, Collection]:
    df, scheme_name = julius_app.local_dfs.get(id)
    if scheme_name_to is None:
        return df, LocalCollection(id)
    return await __get_df_with_update(df, scheme_name, scheme_name_to, julius_app.debug_mode, julius_app.operation_id, julius_app.logs_buffer), LocalCollection(id)


async def get_df_share(julius_app, id: str, scheme_name_to: Optional[str]) -> Tuple[dd.DataFrame, Collection]:
    df, scheme, metadata = get_collection_dask(id, julius_app.operation_id)
    scheme_name = scheme["schemeName"] if scheme is not None and "schemeName" in scheme else None
    if scheme_name_to is not None:
        df = await __get_df_with_update(df, scheme_name, scheme_name_to, julius_app.debug_mode, julius_app.operation_id, julius_app.logs_buffer)
    collection = save_df_local(julius_app, df, scheme_name_to)
    julius_app.metadata[collection.get()] = metadata
    return df, collection


def save_dask_collection(df: dd.DataFrame, operation_id: str, fix_scheme: Optional[FixScheme] = None) -> str:
    df = df.drop(["__id__", "__name__"], axis=1, errors="ignore")
    df["__name__"] = df.apply(lambda _: "", axis=1, meta=(None, 'str'))
    df["__id__"] = df.apply(lambda _: str(uuid4()), axis=1, meta=(None, 'str'))
    collection_id = save_collection_dask(df, operation_id, None if fix_scheme is None else fix_scheme.model_dump())
    return collection_id


def save_collection(df: dd.DataFrame, operation_id: str, fix_scheme: Optional[FixScheme]) -> Collection:
    collection_id = save_dask_collection(df, operation_id, fix_scheme)
    return ShareCollection(collection_id)


def save_df_local(julius_app, df: dd.DataFrame, scheme_name: Optional[str] = None) -> Collection:
    id = julius_app.local_dfs.post(df, scheme_name)
    return LocalCollection(id)
