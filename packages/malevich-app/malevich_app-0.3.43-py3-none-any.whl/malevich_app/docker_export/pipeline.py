from logging import Logger
from typing import List, Tuple, Optional, Dict, Union
import pandas as pd
from asyncio import gather
from pydantic import BaseModel
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import FixScheme
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import JDF, OBJ, DFS, Sink, dfs_many_fun, DF, Doc, Docs
from malevich_app.export.request.core_requests import save_real_collection
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.LogHelper import log_debug
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.helpers import save_object_collection, save_doc, save_collection
from .Interpreter import interpret
from .operations import save_df_local


async def run_processor(julius_app, jdfs_list: List[JDF], logger: Logger) -> Tuple[bool, Optional[Union[List[Tuple[Collection]], callable]]]:
    # jdfs_list, collections_list = await pipeline_interpret(julius_app, collections)
    # julius_app.update_metadata(collections_list)

    collections = []
    log_debug(f"{julius_app._processor_id} in {julius_app.app_id} started", logger)
    update_fun = julius_app.get_scale_part if julius_app.get_scale_part_all else (lambda x: x)

    success, new_dfs = await julius_app.run(*[update_fun(jdf) for jdf in jdfs_list])
    if not success:
        return False, new_dfs   # there: new_dfs - traceback str

    log_debug(f"{julius_app._processor_id} in {julius_app.app_id} finished", logger)

    if julius_app.is_stream():
        assert callable(new_dfs), "stream processor should return callable"
        collections = new_dfs
    else:
        if isinstance(new_dfs, Tuple) or isinstance(new_dfs, DFS) or isinstance(new_dfs, List) and len(new_dfs) > 0 and\
                all(map(lambda df: isinstance(df, pd.DataFrame) or isinstance(df, OBJ) or isinstance(df, Docs) or isinstance(df, List), new_dfs)):
            for new_df_i in new_dfs:
                if isinstance(new_df_i, OBJ):
                    collections.append((save_object_collection(julius_app, new_df_i),))
                else:
                    assert isinstance(new_df_i, pd.DataFrame) or isinstance(new_df_i, Doc) or isinstance(new_df_i, Docs) or issubclass(new_df_i.__class__, BaseModel) or isinstance(new_df_i, Dict) or isinstance(new_df_i, List), f"processor should return pd.DataFrame/OBJ/Doc/Docs/BaseModel/Dict or list/tuple/DFS of them, found {type(new_df_i)}"
                    collections.append((save_df_local(julius_app, new_df_i),))
        else:
            if isinstance(new_dfs, OBJ):
                collections.append((save_object_collection(julius_app, new_dfs),))
            else:
                assert isinstance(new_dfs, pd.DataFrame) or isinstance(new_dfs, Doc) or isinstance(new_dfs, Docs) or issubclass(new_dfs.__class__, BaseModel) or isinstance(new_dfs, Dict) or isinstance(new_dfs, List), f"processor should return pd.DataFrame/OBJ/Doc/Docs/BaseModel/Dict or list/tuple/DFS of them, found {type(new_dfs)}"
                collections.append((save_df_local(julius_app, new_dfs),))

    return True, collections


async def run_condition(julius_app, jdfs_list: List[JDF], logger: Logger) -> Tuple[bool, bool]:
    # jdfs_list, collections_list = await pipeline_interpret(julius_app, collections)
    # julius_app.update_metadata(collections_list)

    log_debug(f"{julius_app._condition_id} in {julius_app.app_id} started", logger)
    success, res = await julius_app.run(*jdfs_list)
    if not success:
        return False, res
    else:
        log_debug(f"{julius_app._condition_id} in {julius_app.app_id} finished", logger)
        return True, res


async def run_output(julius_app, collections: List[Tuple[Collection]], logger: Logger) -> Tuple[bool, List[Collection]]:
    previous_operation = julius_app.get_operation()
    julius_app.set_operation(EntityType.OUTPUT)
    if not julius_app.output_fun_exists():  # TODO not change collections if not exists output and they used only locally
        # not really know now, is derived from what has come
        schemes_info = ([(dfs_many_fun, ("*",))], None, None)
        julius_app._update_schemes_info(schemes_info, EntityType.OUTPUT)
    jdfs_list, collections_list = await interpret(julius_app, collections)  # FIXME other specific interpret, move result schemes to processor
    julius_app.update_metadata(collections_list)
    schemes_info = (await julius_app.get_schemes_info())[0]

    collections: List[Collection] = []
    if julius_app.kafka_helper is None:
        for jdf, (_, scheme) in zip(jdfs_list, schemes_info):
            if scheme == ("*",):
                scheme = None
            if isinstance(jdf, DF):
                collections.append(save_collection(jdf, julius_app.operation_id, fix_scheme=None if scheme is None or scheme[0] is None else FixScheme(schemeName=scheme[0], mode="not_check")))
            elif isinstance(jdf, OBJ):
                collections.append(save_object_collection(julius_app, jdf))
            elif isinstance(jdf, Sink):
                raise Exception(f"Sink argument not supported for output")
            elif isinstance(jdf, Doc) or isinstance(jdf, Docs):
                collections.append(save_doc(jdf, julius_app.operation_id, fix_scheme=None if scheme is None or scheme[0] is None else FixScheme(schemeName=scheme[0], mode="not_check")))
            else:
                assert isinstance(jdf, DFS), "internal error: output wrong df type"
                if scheme is None:
                    scheme = [None] * len(jdf)
                else:
                    assert len(jdf) == len(scheme), f"internal error: wrong schemes count {scheme}"
                for df, subscheme in zip(jdf, scheme):
                    if isinstance(df, DF):
                        collections.append(save_collection(df, julius_app.operation_id, fix_scheme=None if subscheme is None or subscheme[0] is None else FixScheme(schemeName=subscheme[0], mode="not_check")))
                    elif isinstance(df, OBJ):
                        collections.append(save_object_collection(julius_app, df))
                    elif isinstance(df, Sink):
                        raise Exception(f"Sink argument not supported for output")
                    elif isinstance(df, Doc) or isinstance(df, Docs):
                        collections.append(save_doc(df, julius_app.operation_id, fix_scheme=None if scheme is None or scheme[0] is None else FixScheme(schemeName=scheme[0], mode="not_check")))
                    else:
                        assert isinstance(df, DFS), "internal error: output wrong df type"
                        for df_i in df:
                            if isinstance(df_i, OBJ):
                                collections.append(save_object_collection(julius_app, df_i))
                            elif isinstance(df_i, Sink):
                                raise Exception(f"internal error: Sink argument not supported for output")
                            elif isinstance(df_i, Doc) or isinstance(df_i, Docs):
                                collections.append(save_doc(df_i, julius_app.operation_id, fix_scheme=None if scheme is None or scheme[0] is None else FixScheme(schemeName=scheme[0], mode="not_check")))
                            else:
                                collections.append(save_collection(df_i, julius_app.operation_id, fix_scheme=None if subscheme is None or subscheme[0] is None else FixScheme(schemeName=subscheme[0], mode="not_check")))
    else:
        for_produce_collections = []
        for jdf, (_, scheme) in zip(jdfs_list, schemes_info):
            if isinstance(jdf, DF):
                if scheme is not None:
                    assert len(scheme) == 1, f"output wrong schemes count (should be 1): {scheme}"
                for_produce_collections.append((jdf, scheme if scheme is None else scheme[0]))
            elif isinstance(jdf, Sink):
                raise Exception(f"Sink argument not supported for output")
            elif isinstance(jdf, OBJ):
                for_produce_collections.append((jdf.as_df, scheme if scheme is None else scheme[0]))
            elif isinstance(jdf, Doc) or isinstance(jdf, Docs):
                for_produce_collections.append((jdf.parse(), scheme if scheme is None else scheme[0]))
            else:
                assert isinstance(jdf, DFS), "internal error: output wrong df type"
                if scheme is None:
                    scheme = [None] * len(jdf)
                else:
                    assert len(jdf) == len(scheme), f"internal error: wrong schemes count {scheme}"
                for df, subscheme in zip(jdf, scheme):
                    if isinstance(df, DF):
                        for_produce_collections.append((df, subscheme if subscheme is None else subscheme[0]))
                    elif isinstance(df, Sink):
                        raise Exception(f"Sink argument not supported for output")
                    elif isinstance(df, OBJ):
                        for_produce_collections.append((df.as_df, subscheme if subscheme is None else subscheme[0]))
                    elif isinstance(df, Doc) or isinstance(df, Docs):
                        for_produce_collections.append((df.parse(), scheme if scheme is None else scheme[0]))
                    else:
                        assert isinstance(df, DFS), "internal error: output wrong df type"
                        for df_i in df:
                            for_produce_collections.append((df_i, subscheme if subscheme is None else subscheme[0]))
        collections = await julius_app.kafka_helper.produce(for_produce_collections)

    core_saved_collections = None
    if julius_app.collection_out_names is not None and julius_app.kafka_helper is None:  # TODO not save if used kafka?
        if len(julius_app.collection_out_names) != len(collections):
            raise EntityException(f"wrong output arguments count, it should be len(collection_names)={len(julius_app.collection_out_names)}")
        tasks = []
        for i, (collection, collection_name) in enumerate(zip(collections, julius_app.collection_out_names)):
            tasks.append(save_real_collection(collection, julius_app, collection_name, i))
        core_saved_collections = list(await gather(*tasks))
    if julius_app.save_collections_name is not None:
        group_name = None
        save_collections_names = julius_app.save_collections_name
        if len(save_collections_names) != len(collections):
            if len(save_collections_names) != 1:
                raise EntityException(f"save collection failed - wrong names size: expected {len(collections)}, found {len(julius_app.save_collections_name)}")
            group_name = save_collections_names[0]
            save_collections_names = [f"{group_name}_{i}" for i in range(len(collections))]
        elif len(save_collections_names) == 1:
            group_name = save_collections_names[0]
        tasks = []
        for i, (collection, collection_name) in enumerate(zip(collections, save_collections_names)):
            tasks.append(save_real_collection(collection, julius_app, collection_name, i, group_name=group_name))
        temp = await gather(*tasks)
        if core_saved_collections is None:
            core_saved_collections = list(temp)
    if core_saved_collections is None and C.IS_EXTERNAL:
        tasks = []
        for i, collection in enumerate(collections):
            if isinstance(collection, ObjectCollection):
                # FIXME
                julius_app.logs_buffer.write(f"object collection not supported for external apps, path=\"{collection.get()}\"\n")
            tasks.append(save_real_collection(collection, julius_app, None, i))
        core_saved_collections = list(await gather(*tasks))
    if julius_app.output_fun_exists():  # ignore result
        log_debug(f"{julius_app._output_id} in {julius_app.app_id} started", logger)
        success, _ = await julius_app.run(*jdfs_list)   # FIXME ???
        if success:
            log_debug(f"{julius_app._output_id} in {julius_app.app_id} finished", logger)
        else:
            julius_app.logs_buffer.write("warning: output function failed\n")
    if C.IS_EXTERNAL:
        collections = core_saved_collections

    julius_app.set_operation(previous_operation)
    return True, collections
