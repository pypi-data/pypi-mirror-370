from asyncio import gather
import dask.dataframe as dd
from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel
from malevich_app.export.abstract.abstract import FixScheme
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import JDF, OBJ
from malevich_app.export.jls.helpers import get_schemes_info
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.FileCollection import FileCollection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.collection.MongoCollection import MongoCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.collection.ShareCollection import ShareCollection
from malevich_app.export.secondary.helpers import get_df_object
from .operations import get_df, get_df_local, get_df_share, get_df_object_record


async def interpret(julius_app, collections: List[Tuple[Collection, ...]]) -> Tuple[List[JDF], List[Tuple[Collection, ...]]]:
    async def __get_df(collection: Collection, scheme: Optional[str]) -> Tuple[dd.DataFrame, Collection]:
        julius_app.check_collection(collection, scheme)
        if isinstance(collection, MongoCollection):
            assert scheme != OBJ.__name__, f"set collection instead path for OBJ: {collection.get()}"
            df, coll = await get_df(julius_app, collection.get(), None if scheme is None else FixScheme(schemeName=scheme, mode=collection.get_mode()))
        elif isinstance(collection, ShareCollection) or isinstance(collection, FileCollection):
            df, coll = await get_df_share(julius_app, collection.get(), scheme)
        elif isinstance(collection, LocalCollection):
            df, coll = await get_df_local(julius_app, collection.get(), scheme)
        elif isinstance(collection, ObjectCollection):
            if scheme == OBJ.__name__ or (julius_app.get_operation() == EntityType.OUTPUT and not julius_app.output_fun_exists() and scheme is None):
                df, coll = await get_df_object(julius_app, collection.get())
            else:
                assert scheme is None or scheme == "obj", f"wrong conversation: DF from OBJ, scheme should be None, Any or \"obj\", found {scheme}"
                # if julius_app.get_operation() == EntityType.OUTPUT:
                #     await save_collections(julius_app, [collection])
                df, coll = await get_df_object_record(julius_app, collection.get())
        else:
            raise Exception("wrong Collection type")
        if julius_app.need_drop_internal and not isinstance(df, str) and not isinstance(df, Dict) and not isinstance(df, List) and not issubclass(df.__class__, BaseModel):  # for OBJ and Doc
            df.drop("__id__", axis=1, inplace=True, errors='ignore')
            df.drop("__name__", axis=1, inplace=True, errors='ignore')
        return df, coll

    schemes_info, sink_index = await get_schemes_info(julius_app, collections)
    if sink_index is not None and julius_app.start_processor_context_pos():
        sink_index -= 1
    if len(schemes_info) != len(collections) and sink_index is None:  # only for DFS[M[..]] in output
        assert all(map(lambda x: len(x) == 1, collections)), "internal error: output DFS[M[..]] wrong configuration"
        collections = [tuple([collection_tuple[0] for collection_tuple in collections])]
    assert sink_index is None or len(collections) >= len(schemes_info) - 1, f"too few collections, expected at least {len(schemes_info) - 1}, found {len(collections)}"

    tasks = []
    if sink_index is not None:
        all_schemes_info = schemes_info[:sink_index] + schemes_info[sink_index:sink_index + 1] * (len(collections) - len(schemes_info) + 1) + schemes_info[sink_index + 1:]
    else:
        all_schemes_info = schemes_info
    for i, (collection, (_, scheme)) in enumerate(zip(collections, all_schemes_info)):
        if scheme is None:
            scheme = [None] * len(collection)
        else:
            temp_scheme = []
            for subscheme in scheme:
                if subscheme is not None and subscheme.endswith("*"):
                    subscheme = subscheme[:-1] if len(subscheme) > 1 else None
                    for _ in range(len(collection) - len(scheme) + 1):
                        temp_scheme.append(subscheme)
                else:
                    temp_scheme.append(subscheme)
            scheme = temp_scheme
            assert len(collection) == len(scheme), f"wrong function arguments: invalid subarguments number in {i} tuple argument: expected {len(scheme)}, found {len(collection)}"
        subtasks = []
        for j, (subcollection, subscheme) in enumerate(zip(collection, scheme)):
            assert isinstance(subcollection, Collection), f"wrong function arguments: invalid {j} subargument in {i} tuple argument: not collection"
            subtasks.append(__get_df(subcollection, subscheme))
        tasks.append(gather(*subtasks))

    list_dfs_temp = []
    list_collections_res: List[Tuple[Collection, ...]] = []
    for i, argument in enumerate(await gather(*tasks)):
        dfs = []
        collections_res = []
        for df, collection_res in argument:
            dfs.append(df)
            collections_res.append(collection_res)
        list_dfs_temp.append(dfs)
        list_collections_res.append(tuple(collections_res))

    list_dfs: List[JDF] = []
    if sink_index is not None:
        for i, dfs in enumerate(list_dfs_temp[:sink_index]):
            list_dfs.append(schemes_info[i][0](*dfs))

        sink_count = len(collections) - len(schemes_info) + 1
        list_dfs.append(schemes_info[sink_index][0](*list_dfs_temp[sink_index:sink_index + sink_count]))

        for i, dfs in enumerate(list_dfs_temp[sink_index + sink_count:]):
            list_dfs.append(schemes_info[sink_index + 1 + i][0](*dfs))
    else:
        for i, dfs in enumerate(list_dfs_temp):
            list_dfs.append(schemes_info[i][0](*dfs))
    return list_dfs, list_collections_res
