import io
import pandas as pd
from typing import Dict, Optional, List, Tuple, Callable, Any, Union, Set
from asyncio import gather, Lock
from mypy_extensions import VarArg
from pydantic import BaseModel
import malevich_app.export.secondary.const as C
from malevich_app.docker_export.funcs import docker_mode
from malevich_app.docker_export.helpers import LocalDfsSpark
from malevich_app.docker_export.operations import get_df, get_df_share, get_df_local, get_df_object_record, get_doc_data
from malevich_app.export.abstract.abstract import CollectionAndScheme, FixScheme, Cfg
from malevich_app.export.abstract.pipeline import PullCollectionPolicy
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.df import JDF, OBJ
from malevich_app.export.jls.helpers import is_docs_scheme
from malevich_app.export.request.core_requests import post_request_json
from malevich_app.export.secondary.LocalDfs import LocalDfs
from malevich_app.export.secondary.EntityException import LOAD_COLLECTION_FAIL_MSG, EntityException
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.CompositeCollection import CompositeCollection
from malevich_app.export.secondary.collection.ComputeCollection import ComputeCollection
from malevich_app.export.secondary.collection.FileCollection import FileCollection
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.collection.MongoCollection import MongoCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.collection.PromisedCollection import PromisedCollection
from malevich_app.export.secondary.collection.ShareCollection import ShareCollection
from malevich_app.export.secondary.collection.VariantCollection import VariantCollection
from malevich_app.export.secondary.endpoints import MONGO_LOAD
from malevich_app.export.secondary.helpers import get_collection_pandas, get_df_object, get_collection_by_id, get_collection_json, DocsRaw, VariantList


class JuliusCollectionHolder:   # TODO gc
    def __init__(self, operation_id: str, secret: str, dag_host_port: str, logs_buffer: io.StringIO, pull_policy: PullCollectionPolicy, schemes_aliases: Dict[str, str], internal_schemes: Set[str], storage: Optional['LocalStorage']):
        self.__operation_id = operation_id
        self.__secret = secret
        self.__dag_host_port = dag_host_port
        self.__logs_buffer = logs_buffer
        self.__pull_policy = pull_policy
        self.__schemes_aliases = schemes_aliases
        self.__internal_schemes = internal_schemes
        self.__local_storage = storage
        self.__is_local = storage is not None
        self.__metadata = {}
        self.local_dfs: LocalDfs = LocalDfs() if docker_mode != "pyspark" else LocalDfsSpark()

        self.__internal_id_to_local_df_id: Dict[str, int] = {}                      # internal id -> id in local_dfs; -1 - requested, but not set yet
        self.__collections: Dict[str, Collection] = {}                              # internal id -> used collections

        self.__to_load = {}
        self.__to_load_temp = {}
        self.__mutex = Lock()
        self.__collections_by_bind_id_and_iter: Dict[str, Dict[str, Dict[int, List[PromisedCollection]]]] = {}                  # run_id -> bind_id -> iteration -> collections, used his result
        self.__variant_collections: Dict[str, Dict[int, List[VariantCollection]]] = {}                                          # run_id -> iteration -> []colls
        self.__alt_collections_by_bind_id_and_iter: Dict[str, Dict[str, Dict[int, Dict[Tuple[str, str, int], PromisedCollection]]]] = {}   # part, also exist in __collections_by_bind_id_and_iter

    def __internal_id(self, collection_id: str, scheme: Optional[str]):
        return f"{collection_id}${scheme}"

    def __update_schemes(self, scheme_names: Optional[Tuple[Optional[str], ...]]) -> Optional[Tuple[Optional[str], ...]]:  # one argument
        if scheme_names is None:
            return scheme_names
        assert isinstance(scheme_names, Tuple), f"wrong scheme {scheme_names}"
        res = []
        for scheme_name in scheme_names:
            if scheme_name is not None and scheme_name != "*":
                if scheme_name in self.__schemes_aliases:
                    scheme_name = self.__schemes_aliases[scheme_name]
                if scheme_name in self.__internal_schemes:  # defined with jls.scheme
                    scheme_name = f"{self.__operation_id}_{scheme_name}"
            res.append(scheme_name)
        return tuple(res)

    async def __update_collection(self, id: int, collection_id: str, scheme: Optional[str], force_reload: bool = False):
        if not force_reload:    # FIXME twice in one app
            internal_id = self.__internal_id(collection_id, scheme)
            if self.__internal_id_to_local_df_id[internal_id] != -1:
                return
            else:
                self.__internal_id_to_local_df_id[internal_id] = id

        if self.__is_local:
            new_id = self.__local_storage.get_data(self.__operation_id, collection_id, scheme)
            res = {"result": "" if new_id is None else new_id}
        else:
            fix_scheme = None if scheme is None else FixScheme(schemeName=scheme)
            collection_and_scheme = CollectionAndScheme(operationId=self.__operation_id, collectionId=collection_id, hostedAppId=C.APP_ID, secret=self.__secret, fixScheme=fix_scheme)
            res = await post_request_json(MONGO_LOAD(self.__dag_host_port), collection_and_scheme.model_dump_json(), buffer=self.__logs_buffer, fail_info=f"{LOAD_COLLECTION_FAIL_MSG}: {collection_id}", operation_id=self.__operation_id)
        if collection_id.startswith(JsonCollection.prefix) or is_docs_scheme(scheme):
            df_or_doc, _, metadata = get_collection_json(collection_id, self.__operation_id)
        else:
            if res["result"] != "":     # update collection     # TODO not update id, ok?
                collection_id = res["result"]
            df_or_doc, _, metadata = get_collection_pandas(collection_id, self.__operation_id)
        self.__metadata[id] = metadata
        self.local_dfs.update(id, df_or_doc, scheme)

    def __collections_by_bind_id_struct(self, run_id: str):
        collections_by_bind_id = self.__collections_by_bind_id_and_iter.get(run_id)
        if collections_by_bind_id is None:
            collections_by_bind_id = {}
            self.__collections_by_bind_id_and_iter[run_id] = collections_by_bind_id
        return collections_by_bind_id

    def __alt_collections_by_bind_id_struct(self, run_id: str):
        alt_collections_by_bind_id = self.__alt_collections_by_bind_id_and_iter.get(run_id)
        if alt_collections_by_bind_id is None:
            alt_collections_by_bind_id = {}
            self.__alt_collections_by_bind_id_and_iter[run_id] = alt_collections_by_bind_id
        return alt_collections_by_bind_id

    def add_collection_by_id(self, collection_id: str, scheme: Optional[str], on_start: bool = True) -> Collection:
        internal_id = self.__internal_id(collection_id, scheme)
        if collection_id.startswith(ObjectCollection.prefix):
            coll = ObjectCollection(collection_id)
            self.__collections[internal_id] = coll
            return coll

        id = self.__internal_id_to_local_df_id.get(internal_id)
        if id is not None:
            coll = self.__collections[internal_id]
            if on_start or not (self.__pull_policy == PullCollectionPolicy.FORCE_RELOAD_ALL or self.__pull_policy == PullCollectionPolicy.FORCE_RELOAD):
                return coll
        else:
            self.__internal_id_to_local_df_id[internal_id] = -1
            id = self.local_dfs.post()
            coll = LocalCollection(id, is_doc=collection_id.startswith(JsonCollection.prefix) or is_docs_scheme(scheme))
            self.__collections[internal_id] = coll

        if on_start:
            if self.__pull_policy == PullCollectionPolicy.FORCE_RELOAD_ALL:
                if id not in self.__to_load:
                    self.__to_load[id] = self.__update_collection(id, collection_id, scheme, True)
            else:
                if id not in self.__to_load_temp:
                    self.__to_load_temp[id] = self.__update_collection(id, collection_id, scheme)
        else:
            if id not in self.__to_load_temp:
                force_reload = self.__pull_policy == PullCollectionPolicy.FORCE_RELOAD_ALL or self.__pull_policy == PullCollectionPolicy.FORCE_RELOAD
                self.__to_load_temp[id] = self.__update_collection(id, collection_id, scheme, force_reload)

        return coll

    def add_collection_by_name(self, collection_name: str, scheme: Optional[str]) -> Collection:
        async def add(collections: Dict[str, str]) -> Collection:
            collection_id = collections.get(collection_name)
            if collection_id is None:
                raise EntityException(f"collection with name={collection_name} not exist in config collections")
            return self.add_collection_by_id(collection_id, scheme, False)

        return ComputeCollection(add)

    def add_collection_by_result(self, run_id: str, bind_processor_id_from: str, iteration: int, *, key: Optional[Tuple[str, str, int, Optional[int]]], coll: PromisedCollection) -> Collection:
        collections_by_bind_id_and_iter = self.__collections_by_bind_id_struct(run_id)
        bind_collections_by_iter = collections_by_bind_id_and_iter.get(bind_processor_id_from)
        if bind_collections_by_iter is None:
            bind_collections_by_iter = {}
            collections_by_bind_id_and_iter[bind_processor_id_from] = bind_collections_by_iter

        bind_collections = bind_collections_by_iter.get(iteration)
        if bind_collections is None:
            bind_collections = []
            bind_collections_by_iter[iteration] = bind_collections
        bind_collections.append(coll)

        if key is not None:     # alternative
            alt_collections_by_bind_id_and_iter = self.__alt_collections_by_bind_id_struct(run_id)
            alt_bind_collections_by_iter = alt_collections_by_bind_id_and_iter.get(bind_processor_id_from)
            if alt_bind_collections_by_iter is None:
                alt_bind_collections_by_iter = {}
                alt_collections_by_bind_id_and_iter[bind_processor_id_from] = alt_bind_collections_by_iter

            alt_bind_collections = alt_bind_collections_by_iter.get(iteration)
            if alt_bind_collections is None:
                alt_bind_collections = {}
                alt_bind_collections_by_iter[iteration] = alt_bind_collections
            alt_bind_collections[key] = coll
        return coll

    def get_collection_by_result(self, run_id: str, bind_id: str, iteration: int, key: Tuple[str, str, int, Optional[int]]) -> PromisedCollection:      # need for alternative
        collection: PromisedCollection = self.__alt_collections_by_bind_id_and_iter.get(run_id, {}).get(bind_id, {}).get(iteration, {}).get(key, None)
        assert collection is not None, f"internal error: alternative collection get"
        return collection

    def set_collection_external(self, run_id: str, data: Dict[str, Tuple[str, ...]], bind_id_iterations: Dict[str, int]):
        collections_by_bind_id_and_iter = self.__collections_by_bind_id_struct(run_id)

        for bind_id, colls in data.items():
            promised_collections_by_iter = collections_by_bind_id_and_iter.get(bind_id)
            if promised_collections_by_iter is None:
                continue

            iteration = bind_id_iterations[bind_id]
            promised_collections = promised_collections_by_iter.get(iteration)
            if promised_collections is None:
                continue

            real_collections = [get_collection_by_id(coll) for coll in colls]     # FIXME not mongoCollection
            for promised_collection in promised_collections:
                promised_collection.set_result(real_collections)

    def add_variant_collection(self, run_id: str, iteration: int, collections: List[Tuple[Tuple[Callable[[str, int], Collection], ...], Optional[Dict[str, bool]]]], is_sink: bool) -> VariantCollection:
        coll = VariantCollection(run_id, iteration, collections, is_sink)
        run_variant_collections = self.__variant_collections.get(run_id)
        if run_variant_collections is None:
            run_variant_collections = {}
            self.__variant_collections[run_id] = run_variant_collections

        run_iter_variant_collections = run_variant_collections.get(iteration)
        if run_iter_variant_collections is None:
            run_iter_variant_collections = []
            run_variant_collections[iteration] = run_iter_variant_collections

        run_iter_variant_collections.append(coll)
        return coll

    def __init_tasks(self, on_init: bool = True) -> List[Any]:
        tasks = list(self.__to_load_temp.values())
        self.__to_load_temp.clear()
        if on_init:
            tasks += list(self.__to_load.values())
        return tasks

    async def init(self):
        async with self.__mutex:
            await gather(*self.__init_tasks())

    def done(self, run_id: str, bind_id: str, iteration: int, res: List[Collection]):
        # self.__logs_buffer.write(f"done {bind_id} {iteration}\n")
        collections_by_bind_id_and_iter = self.__collections_by_bind_id_struct(run_id)
        next_collections_by_iter = collections_by_bind_id_and_iter.get(bind_id)
        if next_collections_by_iter is None:
            return

        next_collections = next_collections_by_iter.get(iteration)
        if next_collections is None:
            return

        for coll in next_collections:
            coll.set_result(res)

    def conds(self, run_id: str, iteration: int, conds: Dict[str, bool]):
        # self.__logs_buffer.write(f"conds {run_id} {iteration} {conds}\n")
        for coll in self.__variant_collections.get(run_id, {}).get(iteration, []):
            coll.set_conds(conds)

    async def interpret(self, julius_app, collections: List[Tuple[Union[Tuple[Collection, ...], List[Tuple[Collection, ...]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]], cfg: Cfg) -> Tuple[List[JDF], List[List[Union[LocalCollection, ObjectCollection, CompositeCollection, List[Union[LocalCollection, ObjectCollection, CompositeCollection]]]]]]:
        async def __get_df(collection: Collection, scheme: Union[Optional[str], Tuple[Optional[str]]]) -> Union[Tuple[Union[pd.DataFrame, List[pd.DataFrame]], Collection], List[Tuple[Union[pd.DataFrame, List[pd.DataFrame]], Collection]], VariantList]:
            julius_app.check_collection(collection, scheme)
            if isinstance(collection, MongoCollection):
                collection = collection.base()

            if isinstance(collection, MongoCollection):
                if scheme == OBJ.__name__:
                    raise EntityException(f"set collection instead path for OBJ: {collection.get()} (id={julius_app._processor_id})")
                df, coll = await get_df(julius_app, collection.get(), None if scheme is None else FixScheme(schemeName=scheme, mode=collection.get_mode()))
            elif isinstance(collection, ShareCollection) or isinstance(collection, FileCollection):
                df, coll = await get_df_share(julius_app, collection.get(), scheme)
            elif isinstance(collection, LocalCollection):
                df, coll = await get_df_local(julius_app, collection.get(), scheme)
            elif isinstance(collection, ObjectCollection):
                if scheme == OBJ.__name__ or (julius_app.get_operation() == EntityType.OUTPUT and not julius_app.output_fun_exists() and scheme is None):
                    df, coll = await get_df_object(julius_app, collection.get())
                else:
                    if scheme is not None and scheme != "obj":
                        raise EntityException(f"wrong conversation: DF from OBJ, scheme should be None, Any or \"obj\", found {scheme} (id={julius_app._processor_id})")
                    df, coll = await get_df_object_record(julius_app, collection.get())
            elif isinstance(collection, ComputeCollection):
                return await __get_df(collection.get_collection(), scheme)
            elif isinstance(collection, PromisedCollection):
                colls = collection.get()    # result - CompositeCollection
                if isinstance(scheme, Tuple) or isinstance(scheme, List):
                    if len(colls) != len(scheme):
                        raise EntityException(f"wrong collections size - expected {len(scheme)}({scheme}), found {len(colls)} (id={julius_app._processor_id})")
                else:
                    scheme = [scheme] * len(colls)
                df, subcolls = [], []
                for coll, scheme_i in zip(colls, scheme):
                    df_i, coll_i = await __get_df(coll, scheme_i)
                    df.append(df_i)
                    subcolls.append(coll_i)
                coll = CompositeCollection(subcolls)
            elif isinstance(collection, VariantCollection):
                res = []
                colls = collection.get()
                if isinstance(scheme, Tuple) or isinstance(scheme, List):
                    if len(colls) != len(scheme):
                        if len(colls) == 1 and isinstance(colls[0], PromisedCollection):
                            scheme = [scheme]
                        else:
                            raise EntityException(f"wrong collections size - expected {len(scheme)}({scheme}), found {len(colls)} (id={julius_app._processor_id})")
                else:
                    scheme = [scheme] * len(colls)

                for coll_i, scheme_i in zip(colls, scheme):
                    res.append(await __get_df(coll_i, scheme_i))
                if collection.is_sink():
                    for i, subres in enumerate(res):
                        res[i] = [subres]
                return VariantList(res)
            elif isinstance(collection, JsonCollection):
                df, coll = await get_doc_data(julius_app, collection.get(with_prefix=True), None if scheme is None else FixScheme(schemeName=scheme, mode=collection.get_mode()))
            else:
                raise Exception("wrong Collection type")

            if df is None:
                raise EntityException(f"internal error: df is None. collection type = {type(coll)}; scheme = {scheme} (id={julius_app._processor_id})")
            if julius_app.need_drop_internal and not isinstance(df, str) and not isinstance(df, Dict) and not isinstance(df, List) and not issubclass(df.__class__, BaseModel):  # for OBJ and Doc and Docs
                df.drop("__id__", axis=1, inplace=True, errors='ignore')
                df.drop("__name__", axis=1, inplace=True, errors='ignore')
            if isinstance(df, List) and isinstance(coll, LocalCollection) and coll.is_doc():
                df = DocsRaw(df)
            return df, coll

        # TODO update_metadata

        tasks = []
        for collection_info in collections:
            for coll in collection_info[0]:
                if isinstance(coll, ComputeCollection):
                    tasks.append(coll.compute(cfg.collections))
                elif isinstance(coll, VariantCollection):
                    for subcoll in coll.get():
                        if isinstance(subcoll, ComputeCollection):
                            tasks.append(subcoll.compute(cfg.collections))
                elif isinstance(coll, Tuple):
                    for subcoll in coll:
                        if isinstance(subcoll, ComputeCollection):
                            tasks.append(subcoll.compute(cfg.collections))
        await gather(*tasks)
        tasks.clear()
        async with self.__mutex:
            await gather(*self.__init_tasks(on_init=False))

        for i, collection_with_info in enumerate(collections):
            arg_collections, _, scheme_info = collection_with_info  # Union[Tuple[Collection, ...], List[Tuple[Collection, ...]]], .., Optional[Tuple[Optional[str], ...]]
            scheme_info = self.__update_schemes(scheme_info)
            subtasks = []
            if scheme_info is None:
                scheme_info = [None] * len(arg_collections)
            else:
                temp_scheme = []
                for subscheme in scheme_info:
                    if subscheme is not None and subscheme.endswith("*"):
                        subscheme = subscheme[:-1] if len(subscheme) > 1 else None
                        for _ in range(len(arg_collections) - len(scheme_info) + 1):
                            temp_scheme.append(subscheme)
                    else:
                        temp_scheme.append(subscheme)
                scheme_info = temp_scheme
            if len(scheme_info) == 1 and len(arg_collections) != len(scheme_info):
                scheme_info = scheme_info * len(arg_collections)

            if len(arg_collections) != len(scheme_info):
                if len(arg_collections) == 1 and (isinstance(arg_collections[0], PromisedCollection) or isinstance(arg_collections[0], VariantCollection)):
                    scheme_info = [scheme_info]
                else:
                    raise EntityException(f"wrong function arguments: invalid subarguments number in {i} tuple argument: expected {len(scheme_info)}, found {len(arg_collections)} (id={julius_app._processor_id})")
            for j, (subcollection, subscheme) in enumerate(zip(arg_collections, scheme_info)):
                if isinstance(subcollection, Tuple):    # sink  # FIXME useless? always len == 1?
                    subsubtasks = []
                    for k, subsubcollection in enumerate(subcollection):
                        if not isinstance(subsubcollection, Collection):
                            raise EntityException(f"wrong function arguments: invalid {k} subsubargument {j} subargument in {i} tuple argument: not collection (id={julius_app._processor_id})")
                        subsubtasks.append(__get_df(subsubcollection, subscheme))
                    subtasks.append(gather(*subsubtasks))
                else:
                    if not isinstance(subcollection, Collection):
                        raise EntityException(f"wrong function arguments: invalid {j} subargument in {i} tuple argument: not collection (id={julius_app._processor_id})")
                    subtasks.append(__get_df(subcollection, subscheme))
            tasks.append(gather(*subtasks))

        res, args_colls = [], []
        for i, argument in enumerate(await gather(*tasks)):
            dfs, colls = [], []
            for temp_arg in argument:
                if isinstance(temp_arg, VariantList):
                    args = temp_arg.get()
                else:
                    args = [temp_arg]
                for arg in args:
                    if isinstance(arg, List):
                        subdfs, subcolls = [], []
                        for sbuarg in arg:
                            df = sbuarg[0]
                            if isinstance(df, List):
                                for subdf in df:
                                    if isinstance(subdf, DocsRaw):
                                        subdfs.append(subdf.get())
                                    else:
                                        subdfs.append(subdf)
                            elif isinstance(df, DocsRaw):
                                subdfs.append(df.get())
                            else:
                                subdfs.append(df)
                            subcolls.append(sbuarg[1])
                        dfs.append(subdfs)
                        colls.append(subcolls)
                    else:
                        df = arg[0]
                        if isinstance(df, List):
                            for subdf in df:
                                if isinstance(subdf, DocsRaw):
                                    dfs.append(subdf.get())
                                else:
                                    dfs.append(subdf)
                        elif isinstance(df, DocsRaw):
                            dfs.append(df.get())
                        else:
                            dfs.append(df)
                        colls.append(arg[1])
            f = collections[i][1]
            res.append(f(*dfs))
            args_colls.append(colls)
        return res, args_colls

    def delete_run(self, run_id: str):
        self.__collections_by_bind_id_and_iter.pop(run_id, None)
        self.__variant_collections.pop(run_id, None)
        self.__alt_collections_by_bind_id_and_iter.pop(run_id, None)
