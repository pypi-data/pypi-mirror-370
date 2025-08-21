import io
from typing import Optional, List, Tuple
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import FixScheme, CollectionAndScheme
from malevich_app.export.request.core_requests import post_request_json, get_mapping_schemes_raw, get_mapping_schemes
from malevich_app.export.secondary.EntityException import LOAD_COLLECTION_FAIL_MSG
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.endpoints import MONGO_LOAD
from malevich_app.export.secondary.helpers import get_collection_pandas, df_columns, obj_df, save_collection


async def get_df(julius_app, spark: SparkSession, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[DataFrame, Collection]:
    collection_and_scheme = CollectionAndScheme(operationId=julius_app.operation_id, collectionId=id, hostedAppId=C.APP_ID, secret=julius_app.secret, fixScheme=fix_scheme)
    res = await post_request_json(MONGO_LOAD(julius_app.dag_host_port), collection_and_scheme.model_dump_json(), buffer=julius_app.logs_buffer, fail_info=LOAD_COLLECTION_FAIL_MSG, operation_id=julius_app.operation_id)
    if res["result"] != "":     # update collection
        id = res["result"]
    df, _, metadata = get_collection_pandas(id, julius_app.operation_id)
    if df.empty:
        spark_df = spark.createDataFrame([], schema=StructType([]))     # TODO(do schema)
    else:
        spark_df = spark.createDataFrame(df)
    julius_app.metadata[id] = metadata
    collection = save_df_local(julius_app, spark_df, None if fix_scheme is None else fix_scheme.schemeName)
    julius_app.metadata[collection.get()] = metadata
    return spark_df, collection


def filter_collection_with_ids(julius_app, id: int, docs_ids: List[str]) -> Collection:
    julius_app.local_dfs.filter(id, docs_ids)
    return LocalCollection(id)


async def __get_df_with_update(df: DataFrame, scheme_name: str, scheme_name_to: str, debug_mode: bool, operation_id: str, buffer: io.StringIO) -> DataFrame:
    mapping = None
    if scheme_name is None:
        columns = df_columns(df)
        if scheme_name_to == "obj" and columns == ["path"]:
            mapping = {"path": "path"}
        else:
            mapping = await get_mapping_schemes_raw(columns, scheme_name_to, operation_id, debug_mode=debug_mode, buffer=buffer)
    elif scheme_name != scheme_name_to:
        mapping = await get_mapping_schemes(scheme_name, scheme_name_to, operation_id, debug_mode=debug_mode, buffer=buffer)

    df = df.toDF(*list(map(str, df.columns)))
    default_columns = []
    for column in ["__name__", "__id__"]:
        if column in df.columns:
            default_columns.append(column)
    if mapping is not None:
        df = df.select(*list(mapping.keys()), *default_columns).toDF(*list(mapping.values()), *default_columns)
    return df


async def get_df_object_record(julius_app, spark: SparkSession, id: str) -> Tuple[DataFrame, Collection]:
    df = obj_df(julius_app, id)
    collection = save_df_local(julius_app, df, None)
    return spark.createDataFrame(df), collection


async def get_df_local(julius_app, id: int, scheme_name_to: Optional[str]) -> Tuple[DataFrame, Collection]:
    df, scheme_name = julius_app.local_dfs.get(id)
    if scheme_name_to is None:
        return df, LocalCollection(id)
    return await __get_df_with_update(df, scheme_name, scheme_name_to, julius_app.debug_mode, julius_app.operation_id, julius_app.logs_buffer), LocalCollection(id)


async def get_df_share(julius_app, spark, id: str, scheme_name_to: Optional[str]) -> Tuple[DataFrame, Collection]:
    df, scheme, metadata = get_collection_pandas(id, julius_app.operation_id)
    df = spark.createDataFrame(df)
    scheme_name = scheme["schemeName"] if scheme is not None and "schemeName" in scheme else None
    if scheme_name_to is not None:
        df = await __get_df_with_update(df, scheme_name, scheme_name_to, julius_app.debug_mode, julius_app.operation_id, julius_app.logs_buffer)
    collection = save_df_local(julius_app, df, scheme_name_to)
    julius_app.metadata[collection.get()] = metadata
    return df, collection


def save_collection_(df: DataFrame, operation_id: str, fix_scheme: Optional[FixScheme]) -> Collection:
    # def row_to_doc_with_name(row: Dict[str, str]) -> DocWithName:
    #      row.pop("__id__", None)
    #      name = row.pop("__name__", "")
    #      data = json.dumps(row, default=pydantic_encoder)
    #      return DocWithName(name=name, data=data)
    #
    # docs_collection_raw = DocsCollectionRaw(data=list(map(lambda row: row_to_doc_with_name(row),
    #                                                     docs.toJSON().map(lambda j: json.loads(j)).collect())))
    # collection = TempCollectionDocs(operationId=julius_app.operation_id, appId=julius_app.app_id, docsCollectionRaw=docs_collection_raw,
    #                                 fixScheme=fix_scheme)
    # collection_id = await post_request_json(DOCS_COLLECTION, collection.model_dump_json())
    # return MongoCollection(collection_id)
    return save_collection(df.toPandas(), operation_id, fix_scheme)


def save_df_local(julius_app, df: DataFrame, scheme_name: Optional[str] = None) -> Collection:
    id = julius_app.local_dfs.post(df, scheme_name)
    return LocalCollection(id)
