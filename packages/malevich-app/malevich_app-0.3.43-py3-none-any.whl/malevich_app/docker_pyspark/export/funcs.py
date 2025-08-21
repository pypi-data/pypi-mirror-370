from asyncio import gather
from pyspark.sql import SparkSession, DataFrame
from logging import Logger
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import FixScheme
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import DF, Sink, OBJ, DFS, JDF, dfs_many_fun, Docs
from malevich_app.export.secondary.LogHelper import log_debug
from malevich_app.export.jls.WrapperMode import InputWrapper
from malevich_app.export.request.core_requests import save_real_collection
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.helpers import save_object_collection, save_collections, get_collection_by_id
from .Interpreter import interpret
from .operations import save_collection_, filter_collection_with_ids, save_df_local
from typing import List, Tuple, Optional, Any, Dict

spark = SparkSession.builder.appName("SparkSession").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
docker_mode = "pyspark"

# FIXME (do it in a similar way to docker_python)


async def input_fun(julius_app, collections: List[Tuple[str, ...]], logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    def split_df(spark: SparkSession, df: DataFrame) -> List[DataFrame]:
        columns = df.columns
        return [spark.createDataFrame([row], columns) for row in df.collect()]

    async def __input_fun(collections) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]]]:
        julius_app.set_operation(EntityType.INPUT)
        if collections:     # use ids from file only at the beginning otherwise
            temp = []
            for subcollections in collections:
                temp.append(tuple(map(get_collection_by_id, subcollections)))
            julius_app.set_collections(temp)
        collections = julius_app._with_extra_collections()
        assert all([x is not None for x in collections]), f"collection not found in config (app id={julius_app.app_id})"

        if not julius_app.input_fun_exists():
            julius_app.set_collections(collections)
            return True, []
        schemes_info = (await julius_app.get_schemes_info())[0]
        schemes_names = [x[1] for x in schemes_info]

        input_mode = julius_app.get_input_mode()
        if input_mode == InputWrapper.INPUT_TRUE:
            if not (len(schemes_names) == 0 or (len(schemes_names) == 1 and schemes_names[0] != C.CONTEXT)):
                assert False, f"\"input_true\" must have no parameters or only Context (app id={julius_app.app_id})"
            julius_app.set_collections(collections)
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} started", logger)
            success, _ = await julius_app.run()
            if not success:
                return False, schemes_names
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} finished", logger)
            return True, schemes_names
        jdfs_list, collections_list = await interpret(julius_app, collections)
        julius_app.update_metadata(collections_list)

        argv = [None for _ in range(len(jdfs_list))]
        collections = []
        if input_mode == InputWrapper.INPUT_DOC:
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} started", logger)
            for i, jdf in enumerate(jdfs_list):
                if isinstance(jdf, DF):
                    assert len(collections_list[i]) == 1, "input: internal error - wrong collections size"
                    df_collection = collections_list[i][0]
                    ids = []
                    for row in split_df(spark, jdf):
                        argv[i] = row
                        success, res = await julius_app.run(*argv)
                        if not success:
                            return False, schemes_names
                        if res:
                            ids.append(row.select("__id__").collect()[0]["__id__"])
                        argv[i] = None
                    collection = filter_collection_with_ids(julius_app, df_collection.get(), ids)
                    collections.append((collection,))
                elif isinstance(jdf, Sink):
                    raise Exception(f"Sink argument not supported for input mode {input_mode}")
                elif isinstance(jdf, OBJ):
                    raise Exception(f"OBJ argument not supported for input mode {input_mode}")
                else:
                    assert isinstance(jdf, DFS), "internal error: input wrong df type"
                    subargv = [None for _ in range(len(jdf))]
                    subcollections = []
                    for j, df in enumerate(jdf):
                        df_collection = collections_list[i][j]
                        subids = []
                        for row in split_df(spark, df):
                            subargv[j] = row
                            argv[i] = subargv
                            success, res = await julius_app.run(*argv)
                            if not success:
                                return False, schemes_names
                            if res:
                                subids.append(df.select("__id__").collect()[0]["__id__"])
                            argv[i] = None
                            subargv[j] = None
                        subcollection = filter_collection_with_ids(julius_app, df_collection.get(), subids)
                        subcollections.append(subcollection)
                    collections.append(tuple(subcollections))
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} finished", logger)
        elif input_mode == InputWrapper.INPUT_DF:
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} started", logger)
            for i, jdf in enumerate(jdfs_list):
                if isinstance(jdf, DF):
                    assert len(collections_list[i]) == 1, "input: internal error - wrong collections size"
                    df_collection = collections_list[i][0]
                    argv[i] = jdf
                    success, ids = await julius_app.run(*argv)
                    if not success:
                        return False, schemes_names
                    argv[i] = None
                    collection = filter_collection_with_ids(julius_app, df_collection.get(), list(ids))
                    collections.append((collection,))
                elif isinstance(jdf, Sink):
                    raise Exception(f"Sink argument not supported for input mode {input_mode}")
                elif isinstance(jdf, OBJ):
                    raise Exception(f"OBJ argument not supported for input mode {input_mode}")
                else:
                    assert isinstance(jdf, DFS), "internal error: input wrong df type"
                    subcollections = []
                    if julius_app.input_df_by_args:
                        argv[i] = jdf
                        success, ids_list = await julius_app.run(*argv)
                        if not success:
                            return False, schemes_names
                        argv[i] = None

                        df_collections = collections_list[i]
                        assert len(ids_list) == len(df_collections), f"wrong input result collections size: expected {len(df_collections)}, found {len(ids_list)}"
                        for ids, df_collection in zip(ids_list, df_collections):
                            subcollection = filter_collection_with_ids(julius_app, df_collection.get(), list(ids))
                            subcollections.append(subcollection)
                    else:
                        subargv = [None for _ in range(len(jdf))]
                        for j, df in enumerate(jdf):
                            df_collection = collections_list[i][j]
                            subargv[j] = df
                            argv[i] = subargv
                            success, ids = await julius_app.run(*argv)
                            if not success:
                                return False, schemes_names
                            argv[i] = None
                            subargv[j] = None
                            subcollection = filter_collection_with_ids(julius_app, df_collection.get(), list(ids))
                            subcollections.append(subcollection)
                    collections.append(tuple(subcollections))
            log_debug(f"{julius_app._input_id} in {julius_app.app_id} finished", logger)
        else:
            raise Exception(f"wrong input mode {input_mode}")

        julius_app.set_collections(collections)
        return True, schemes_names
    ok, schemes_names = await __input_fun(collections)
    return ok, schemes_names, {}


async def processor_fun(julius_app, logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    async def __processor_fun() -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]]]:
        julius_app.set_operation(EntityType.PROCESSOR)

        jdfs_list, collections_list = await interpret(spark, julius_app, julius_app.collections)
        julius_app.update_metadata(collections_list)

        collections = []
        schemes_info = (await julius_app.get_schemes_info())[0]
        schemes_names = [x[1] for x in schemes_info]
        log_debug(f"{julius_app._processor_id} in {julius_app.app_id} started", logger)
        update_fun = julius_app.get_scale_part if julius_app.get_scale_part_all else (lambda x: x)

        success, new_dfs = await julius_app.run(*[update_fun(jdf) for jdf in jdfs_list])
        if not success:
            return False, schemes_names
        log_debug(f"{julius_app._processor_id} in {julius_app.app_id} finished", logger)
        if isinstance(new_dfs, Tuple) or isinstance(new_dfs, DFS) or isinstance(new_dfs, List) and len(new_dfs) > 0 and\
                all(map(lambda df: isinstance(df, DataFrame) or isinstance(df, OBJ) or isinstance(df, Docs) or isinstance(df, List), new_dfs)):
            for new_df_i in new_dfs:
                if isinstance(new_df_i, OBJ):
                    collections.append((save_object_collection(julius_app, new_df_i),))
                else:
                    assert isinstance(new_df_i, DataFrame), f"processor should return DataFrame/OBJ or list/tuple/DFS of them, found {new_df_i}"
                    collections.append((save_df_local(julius_app, new_df_i),))
        else:
            if isinstance(new_dfs, OBJ):
                collections.append((save_object_collection(julius_app, new_dfs),))
            else:
                assert isinstance(new_dfs, DataFrame), f"processor should return DataFrame/OBJ or list/tuple/DFS of them, found {type(new_dfs)}"
                collections.append((save_df_local(julius_app, new_dfs),))
        julius_app.set_collections(collections)
        return True, schemes_names
    ok, schemes_names = await __processor_fun()
    return ok, schemes_names, {}


async def output_fun(julius_app, logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    async def __output_fun() -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], List[Collection]]:
        async def user_output_fun(jdfs_list: List[JDF]) -> bool:
            log_debug(f"{julius_app._output_id} in {julius_app.app_id} started", logger)
            success, _ = await julius_app.run(*jdfs_list)
            if success:
                log_debug(f"{julius_app._output_id} in {julius_app.app_id} finished", logger)
            return success

        julius_app.set_operation(EntityType.OUTPUT)
        if not julius_app.output_fun_exists():
            # not really know now, is derived from what has come
            schemes_info = ([(dfs_many_fun, ("*",))], None, None)
            julius_app._update_schemes_info(schemes_info, EntityType.OUTPUT)
        jdfs_list, collections_list = await interpret(spark, julius_app, julius_app.collections)
        julius_app.update_metadata(collections_list)
        schemes_info = (await julius_app.get_schemes_info())[0]

        if not julius_app.continue_after_processor and julius_app.output_fun_exists():
            ok = await user_output_fun(jdfs_list)
        else:
            ok = True

        collections: List[Collection] = []
        if julius_app.kafka_helper is None:
            for jdf, (_, scheme) in zip(jdfs_list, schemes_info):
                if isinstance(jdf, DF):
                    collections.append(save_collection_(jdf, julius_app.operation_id, fix_scheme=None if scheme is None or scheme[0] is None else FixScheme(schemeName=scheme[0], mode="not_check")))
                elif isinstance(jdf, OBJ):
                    collections.append(save_object_collection(julius_app, jdf))
                elif isinstance(jdf, Sink):
                    raise Exception(f"Sink argument not supported for output")
                else:
                    assert isinstance(jdf, DFS), "internal error: output wrong df type"
                    if scheme is None:
                        scheme = [None] * len(jdf)
                    else:
                        assert len(jdf) == len(scheme), f"internal error: wrong schemes count {scheme}"
                    for df, subscheme in zip(jdf, scheme):
                        if isinstance(df, DF):
                            collections.append(save_collection_(df, julius_app.operation_id, fix_scheme=None if subscheme is None or subscheme[0] is None else FixScheme(schemeName=subscheme[0], mode="not_check")))
                        elif isinstance(df, OBJ):
                            collections.append(save_object_collection(julius_app, df))
                        elif isinstance(df, Sink):
                            raise Exception(f"Sink argument not supported for output")
                        else:
                            assert isinstance(df, DFS), "internal error: output wrong df type"
                            for df_i in df:
                                if isinstance(df_i, OBJ):
                                    collections.append(save_object_collection(julius_app, df_i))
                                else:
                                    collections.append(save_collection_(df_i, julius_app.operation_id, fix_scheme=None if subscheme is None or subscheme[0] is None else FixScheme(schemeName=subscheme[0], mode="not_check")))
        elif julius_app.continue_after_processor or ok:
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
                        else:
                            assert isinstance(df, DFS), "internal error: output wrong df type"
                            for df_i in df:
                                for_produce_collections.append((df_i, subscheme if subscheme is None else subscheme[0]))
            collections = await julius_app.kafka_helper.produce(for_produce_collections)

        schemes_names = [x[1] for x in schemes_info]
        if julius_app.collection_out_names is not None and julius_app.kafka_helper is None:  # TODO not save if used kafka?
            assert len(julius_app.collection_out_names) == len(collections), f"wrong output arguments count, it should be len(collection_names)={len(julius_app.collection_out_names)}"
            tasks = []
            for i, (collection, collection_name) in enumerate(zip(collections, julius_app.collection_out_names)):
                tasks.append(save_real_collection(collection, julius_app, collection_name, i))
            await gather(*tasks)
        if julius_app.save_collections_name is not None:
            group_name = None
            save_collections_names = julius_app.save_collections_name
            if len(save_collections_names) != len(collections):
                assert len(save_collections_names) == 1, f"save collection failed - wrong names size: expected {len(collections)}, found {len(julius_app.save_collections_name)}"
                group_name = save_collections_names[0]
                save_collections_names = [f"{group_name}_{i}" for i in range(len(collections))]
            elif len(save_collections_names) == 1:
                group_name = save_collections_names[0]
            tasks = []
            for i, (collection, collection_name) in enumerate(zip(collections, save_collections_names)):
                tasks.append(save_real_collection(collection, julius_app, collection_name, i, group_name=group_name))
            await gather(*tasks)
        if julius_app.continue_after_processor and julius_app.output_fun_exists():  # ignore result
            ok_ignored = await user_output_fun(jdfs_list)
            if not ok_ignored:
                julius_app.logs_buffer.write("warning: output function failed\n")
        if ok and C.IS_EXTERNAL:
            collection_objects_to_save = []
            for colls in collections_list:
                for collection in colls:
                    if isinstance(collection, ObjectCollection):
                        collection_objects_to_save.append(collection)
            await save_collections(julius_app, collections + collection_objects_to_save)  # collections: OBJ _is_new always False
        return ok, schemes_names, collections
    ok, schemes_names, collections = await __output_fun()
    return ok, schemes_names, {"result": list(map(lambda x: str(x.get(with_prefix=True)) if isinstance(x, ObjectCollection) else str(x.get()), collections))}
