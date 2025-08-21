import asyncio
import copy
import io
import traceback
import pandas as pd
from typing import Dict, Optional, List, Tuple, Callable, Set, Union, Any, Coroutine
from asyncio import gather
from mypy_extensions import VarArg
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import PipelineApp, InitPipeline, InitRun, PipelineStructureUpdate
from malevich_app.export.abstract.pipeline import BaseArgument, PullCollectionPolicy, Argument, AlternativeArgument
from malevich_app.export.jls.EntityType import EntityType
from malevich_app.export.jls.JuliusCollectionHolder import JuliusCollectionHolder
from malevich_app.export.jls.JuliusPipelineItem import JuliusPipelineItem
from malevich_app.export.jls.JuliusTracker import JuliusTracker
from malevich_app.export.jls.RunLoopStructures import RunLoopStructures
from malevich_app.export.jls.StructureUpdate import StructureUpdate
from malevich_app.export.jls.df import JDF
from malevich_app.export.jls.local import find_clusters, full_next_bind_ids, start_loop_bind_ids, full_wait_bind_ids, fix_clusters
from malevich_app.export.request.core_requests import save_real_collection, post_error_info
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.CompositeCollection import CompositeCollection
from malevich_app.export.secondary.collection.LocalCollection import LocalCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.collection.PromisedCollection import PromisedCollection
from malevich_app.export.secondary.collection.VariantCollection import VariantCollection
from malevich_app.export.secondary.creator import do_cfg
from malevich_app.export.secondary.fail_storage import FailStorage, fail_structure
from malevich_app.export.secondary.helpers import get_collection_by_id
from malevich_app.export.secondary.init import get_app_cfg
from malevich_app.export.secondary.structs import DictWrapper

_condition_key = ""

def check(m, k, v):
    assert k not in m or m[k] == v, f"expected {v} for {k}, found {m[k]}: {m}"


class JuliusPipeline:
    def __init__(self, pipeline: InitPipeline, registry, logs_buffer: io.StringIO, pauses: Dict[str, Dict[str, asyncio.Future]], storage: Optional['LocalStorage'] = None, fail_storage: Optional[FailStorage] = None):
        self.__init = pipeline
        self.__registry = registry
        self.__logs_buffer = logs_buffer
        self.__is_local = storage is not None
        self.__fail_storage = fail_storage
        self.__hash = pipeline.hash or ""
        self.__scale_index = pipeline.index     # scale (old) index
        self.__scale = pipeline.pipeline.bindIds
        self.__scaled = max(self.__scale.values()) > 1

        self.dag_host_port = C.DAG_HOST_PORT(pipeline.dagHost)
        self.__common_cfg = do_cfg(pipeline.cfg, pipeline.infoUrl)[0]                                   # cfg
        self.__processor_bind_ids = pipeline.processorIds
        self.__wait_bind_ids: Dict[str, Dict[str, Optional[bool]]] = {}                                 # bindProcessorId | bindConditionId -> bind id -> None (processor), True/False - requirement for condition
        self.__cluster_wait_bind_ids: Dict[int, Dict[str, Dict[str, Optional[bool]]]] = {}              # cluster num -> loop wait_bind_ids part
        self.__wait_bind_ids_conds: Dict[str, List[Dict[str, bool]]] = {}                               # bindProcessorId | bindConditionId -> List (bind id -> None (processor), True/False - requirement for condition)
        self.__cluster_wait_bind_ids_conds: Dict[int, Dict[str, List[Dict[str, bool]]]] = {}            # cluster num -> loop wait_bind_ids_conds part
        self.__alt_wait_bind_ids: Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]] = {}            # bind_id -> arg_name -> i - alt index -> (bind id -> None (processor), True/False - requirement for condition)
        self.__alt_cluster_wait_bind_ids: Dict[int, Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]]] = {}     # as __alt_wait_bind_ids but for loops (and by cluster num)
        self.__nexts: Dict[str, Set[str]] = {}                                                          # bindProcessorId | bindConditionId -> list next bindProcessorId | bindConditionId
        self.__loop_nexts: Dict[str, Set[str]] = {}                                                     # as __nexts but for loops
        self.__nexts_conds: Dict[str, Dict[str, List[Tuple[int, bool]]]] = {}                           # bind_id -> next bind_id -> [](index in conds list, conditon value or None)
        self.__loop_nexts_conds: Dict[str, Dict[str, List[Tuple[int, bool]]]] = {}                      # as __nexts_conds but for loops
        self.__alt_nexts: Dict[str, Dict[str, Dict[str, List[Tuple[int, Optional[bool]]]]]] = {}        # bind_id -> next bind_id -> arg_name -> [](index in alternative arg list, conditon value or None)
        self.__alt_loop_nexts: Dict[str, Dict[str, Dict[str, List[Tuple[int, Optional[bool]]]]]] = {}   # as __alt_nexts but for loops
        self.__alt_deps: Dict[Tuple[str, str, int, str, int], Dict[str, int]] = {}                      # (run_id, bind_id, bind_id iteration, arg_name, index in alternative arg list) -> proc bind_id -> iteration
        self.__collections_holder = JuliusCollectionHolder(pipeline.operationId, pipeline.secret, C.DAG_HOST_PORT(pipeline.dagHost), self.__logs_buffer, pipeline.pipeline.pullCollectionPolicy, self.__common_cfg.schemes_aliases, registry.internal_schemes, storage)
        self.__run_collections_template: Dict[str, List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]]] = {}         # bind_id -> structure, that transforms to collections
        self.__loop_run_collections_template: Dict[str, List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]]] = {}    # bind_id -> structure, that transforms to collections
        self.__bind_ids_list: List[str] = pipeline.bindIdsList
        self.__items: Dict[str, JuliusPipelineItem] = self.__construct()                                # bindProcessorId | bindConditionId -> item (base j_app)

        self.__run_items: Dict[str, Dict[str, JuliusPipelineItem]] = {}                                 # run_id -> bindProcessorId | bindConditionId -> item (j_app)
        self.__run_collections: Dict[str, Dict[str, Dict[int, List[Tuple[Union[Tuple[Collection, ...], List[Tuple[Collection, ...]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]]]]] = {}      # run_id -> bind_id -> iteration -> collections
        self.__run_loop_structures: Dict[str, RunLoopStructures] = {}
        self.__run_wait_bind_ids: Dict[str, Dict[str, Dict[str, Optional[bool]]]] = {}
        self.__run_wait_bind_ids_conds: Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]] = {}
        self.__run_alt_wait_bind_ids: Dict[str, Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]]] = {}

        self.__run_stream_res: Dict[str, Dict[str, callable]] = {}   # run_id -> bind_id -> stream call
        self.__run_pauses: Dict[str, Dict[str, asyncio.Future]] = pauses

        self.__set_collections_next_iteration_by_run_id = {}
        self.__tracker = JuliusTracker(C.DAG_HOST_PORT(pipeline.dagHost), is_local=storage is not None, index=self.__scale_index)
        self.__cur_task = None
        self.__check()

    def reset_hash(self, hash: str):
        # TODO update it in run_items for continue pipeline after reload
        self.__hash = hash

    def scheme_aliases(self):
        return self.__common_cfg.schemes_aliases.keys()

    def set_exist_schemes(self, run_id: Optional[str], schemes_names: Set[str]):
        if run_id is None:
            for item in self.__items.values():
                item.japp.set_exist_schemes(schemes_names)
                break   # schemes_names common for all, so set in 1 enough
        else:
            for item in self.__run_items[run_id].values():
                item.japp.set_exist_schemes(schemes_names)
                break  # schemes_names common for all, so set in 1 enough

    def __check(self):
        assert len(self.__items) > 0, "wrong apps size"
        # TODO

    def __construct(self) -> Dict[str, JuliusPipelineItem]:
        pipeline = self.__init.pipeline
        cfg_collections = self.__common_cfg.collections
        loop_wait_bind_ids: Dict[str, Dict[str, bool]] = {}
        loop_wait_bind_ids_conds: Dict[str, List[Dict[str, bool]]] = {}
        alt_loop_wait_bind_ids: Dict[str, Dict[str, List[Dict[str, bool]]]] = {}

        # set in local run
        if self.__is_local:
            loop_order_deps: Dict[str, Set[str]] = {}
            alt_loop_order_deps: Dict[str, Set[str]] = {}
            bind_ids_list: List[str] = []
            bind_id_to_cluster: Dict[str, int] = {}

        run_collections_template = {}
        self.__run_collections_template = run_collections_template
        loop_run_collections_template = {}
        self.__loop_run_collections_template = loop_run_collections_template
        res = {}

        def arg_collection(run_id: str, iteration: int, arg: BaseArgument, bind_id: str, key: Optional[Tuple[str, str, int, Optional[int]]]) -> PromisedCollection:
            loop_structures = self.__run_loop_structures.get(run_id)
            if loop_structures is None:
                loop_structures = RunLoopStructures(self.__bind_ids_list, self.__init.clusters)
                self.__run_loop_structures[run_id] = loop_structures

            collections_binds = loop_structures.collections_binds_funcs
            binds = collections_binds.get((bind_id, iteration))
            if binds is None:
                binds = {}
                collections_binds[(bind_id, iteration)] = binds

            funcs = binds.get(arg.id)
            if funcs is None:
                funcs = []
                binds[arg.id] = funcs

            coll = PromisedCollection(arg.indices)
            funcs.append(lambda arg_iteration: self.__collections_holder.add_collection_by_result(run_id, arg.id, arg_iteration, key=key, coll=coll))

            return coll

        def update_alt_arg(cur_bind_id: str, bind_id: str, name: str, num: int, cond_value: Optional[bool] = None):
            next = self.__alt_nexts.get(bind_id)
            if next is None:
                next = {}
                self.__alt_nexts[bind_id] = next
            bind_id_next = next.get(cur_bind_id)
            if bind_id_next is None:
                bind_id_next = {}
                next[cur_bind_id] = bind_id_next
            num_conds = bind_id_next.get(name)
            if num_conds is None:
                num_conds = []
                bind_id_next[name] = num_conds
            num_conds.append((num, cond_value))

            name_to_dep_ids_list = self.__alt_wait_bind_ids.get(cur_bind_id)
            if name_to_dep_ids_list is None:
                name_to_dep_ids_list = {}
                self.__alt_wait_bind_ids[cur_bind_id] = name_to_dep_ids_list
            dep_ids_list = name_to_dep_ids_list.get(name)
            if dep_ids_list is None:
                dep_ids_list = []
                name_to_dep_ids_list[name] = dep_ids_list
            for _ in range(num + 1 - len(dep_ids_list)):
                dep_ids_list.append({})
            dep_ids = dep_ids_list[num]
            dep_ids[bind_id] = cond_value

        def update_alt_loop_arg(cur_bind_id: str, bind_id: str, name: str, num: int, cond_value: Optional[bool] = None):
            next = self.__alt_loop_nexts.get(bind_id)
            if next is None:
                next = {}
                self.__alt_loop_nexts[bind_id] = next
            bind_id_next = next.get(cur_bind_id)
            if bind_id_next is None:
                bind_id_next = {}
                next[cur_bind_id] = bind_id_next
            num_conds = bind_id_next.get(name)
            if num_conds is None:
                num_conds = []
                bind_id_next[name] = num_conds
            num_conds.append((num, cond_value))

            name_to_dep_ids_list = alt_loop_wait_bind_ids.get(cur_bind_id)
            if name_to_dep_ids_list is None:
                name_to_dep_ids_list = {}
                alt_loop_wait_bind_ids[cur_bind_id] = name_to_dep_ids_list
            dep_ids_list = name_to_dep_ids_list.get(name)
            if dep_ids_list is None:
                dep_ids_list = []
                name_to_dep_ids_list[name] = dep_ids_list
            for _ in range(num + 1 - len(dep_ids_list)):
                dep_ids_list.append({})
            dep_ids = dep_ids_list[num]
            dep_ids[bind_id] = cond_value

            if self.__is_local:
                cur_loop_order_deps = alt_loop_order_deps.get(cur_bind_id)
                if cur_loop_order_deps is None:
                    cur_loop_order_deps = set()
                    alt_loop_order_deps[cur_bind_id] = cur_loop_order_deps
                cur_loop_order_deps.add(bind_id)

        def add_variant_collection(collections: List[Tuple[Tuple[Callable[[str, int], Collection], ...], Optional[Dict[str, bool]]]], promised_collections_funcs: List[Callable[[str, int], Collection]], is_sink: bool) -> Callable[[str, int], VariantCollection]:
            def internal_add_variant_collection(run_id: str, iteration: int) -> VariantCollection:
                for f in promised_collections_funcs:
                    f(run_id, iteration)
                return self.__collections_holder.add_variant_collection(run_id, iteration, collections, is_sink)
            return internal_add_variant_collection

        def arg_add(arg: BaseArgument, bind_id: str, name: str, scheme_info: Optional[Tuple[Optional[str], ...]], *, first: bool = False, loop: bool = False, is_sink: bool = False, key: Optional[Tuple[str, str, int, Optional[int]]] = None) -> Tuple[Callable[[str, int], Collection], ...]:
            is_alternative = key is not None
            arg.validation()

            if is_alternative:
                if loop:
                    if isinstance(arg, Argument) and arg.conditions is not None:
                        for cond_bind_id, cond_value in arg.conditions.items():
                            update_alt_loop_arg(bind_id, cond_bind_id, name, key[2], cond_value)
                else:
                    if isinstance(arg, Argument) and arg.conditions is not None:
                        for cond_bind_id, cond_value in arg.conditions.items():
                            update_alt_arg(bind_id, cond_bind_id, name, key[2], cond_value)

            if arg.id is not None:
                # TODO add warn: check potential result count
                if arg.indices is not None:
                    if scheme_info is not None and len(arg.indices) != len(scheme_info) and all(map(lambda x: not x.endswith("*"), scheme_info)):
                        raise EntityException(f"wrong subarguments count for argument with name={name} in processor with id={bind_id}: expected {len(scheme_info)} ({scheme_info}), found {len(arg.indices)} ({arg.indices})")
                if loop:
                    if is_alternative:
                        update_alt_loop_arg(bind_id, arg.id, name, key[2])
                    else:
                        next = self.__loop_nexts.get(arg.id)
                        if next is None:
                            next = set()
                            self.__loop_nexts[arg.id] = next
                        next.add(bind_id)

                        dep_ids = loop_wait_bind_ids.get(bind_id)
                        if dep_ids is None:
                            dep_ids = {}
                            loop_wait_bind_ids[bind_id] = dep_ids
                        dep_ids[arg.id] = None

                    return lambda run_id, iteration: arg_collection(run_id, iteration, arg, bind_id, key),
                else:
                    if is_alternative:
                        update_alt_arg(bind_id, arg.id, name, key[2])
                    else:
                        next = self.__nexts.get(arg.id)
                        if next is None:
                            next = set()
                            self.__nexts[arg.id] = next
                        next.add(bind_id)

                        dep_ids = self.__wait_bind_ids.get(bind_id)
                        if dep_ids is None:
                            dep_ids = {}
                            self.__wait_bind_ids[bind_id] = dep_ids
                        dep_ids[arg.id] = None

                    return lambda run_id, iteration: arg_collection(run_id, iteration, arg, bind_id, key),
            elif arg.collectionName is not None:
                if pipeline.pullCollectionPolicy == PullCollectionPolicy.INIT:
                    collection_id = cfg_collections.get(arg.collectionName)     # mb not ok for run - think about it
                    if collection_id is None:
                        raise EntityException(f"collection id not set in cfg by collection name={arg.collectionName} (need for argument with name={name} in processor with id={bind_id})")
                    if scheme_info is not None and len(scheme_info) != 1:
                        raise EntityException(f"collection id not supported for argument with type {scheme_info} (argument with name={name} in processor with id={bind_id})")
                    scheme = None if scheme_info is None else scheme_info[0]
                    return lambda _, __: self.__collections_holder.add_collection_by_id(collection_id, scheme if scheme is None else scheme.removesuffix("*")),
                else:
                    if scheme_info is not None and len(scheme_info) != 1:
                        raise EntityException(f"collection name not supported for argument with type {scheme_info} (argument with name={name} in processor with id={bind_id})")
                    scheme = None if scheme_info is None else scheme_info[0]
                    return lambda _, __: self.__collections_holder.add_collection_by_name(arg.collectionName, scheme if scheme is None else scheme.removesuffix("*")),
            elif arg.collectionId is not None:
                if scheme_info is not None and len(scheme_info) != 1:
                    raise EntityException(f"collection id not supported for argument with type {scheme_info} (argument with name={name} in processor with id={bind_id})")
                scheme = None if scheme_info is None else scheme_info[0]
                return lambda _, __: self.__collections_holder.add_collection_by_id(arg.collectionId, scheme if scheme is None else scheme.removesuffix("*")),
            elif first:
                if isinstance(arg, AlternativeArgument) and arg.alternative is not None:
                    res, promised_collections_funcs = [], []
                    for i, alt_arg in enumerate(arg.alternative):
                        arg_fun = arg_add(alt_arg, bind_id, name, scheme_info, loop=loop, first=True, key=(bind_id, name, i, None), is_sink=is_sink)
                        if alt_arg.id is not None:
                            promised_collections_funcs.append(arg_fun[0])
                            get_arg_fun = lambda run_id, iteration, get_res_bind_id=alt_arg.id, key=(bind_id, name, i, None): self.__collections_holder.get_collection_by_result(run_id, get_res_bind_id, iteration, key=key),
                            res.append((get_arg_fun, alt_arg.conditions))
                        elif alt_arg.group is not None:
                            sub_res = []
                            for j, (sub_alt_arg, sub_arg_fun) in enumerate(zip(alt_arg.group, arg_fun)):
                                if sub_alt_arg.id is not None:
                                    promised_collections_funcs.append(sub_arg_fun)
                                    get_arg_fun = lambda run_id, iteration, get_res_bind_id=sub_alt_arg.id, key=(bind_id, name, i, j): self.__collections_holder.get_collection_by_result(run_id, get_res_bind_id, iteration, key=key)
                                    sub_res.append(get_arg_fun)
                                else:
                                    sub_res.append(sub_arg_fun)
                            res.append((tuple(sub_res), alt_arg.conditions))
                        else:
                            res.append((arg_fun, alt_arg.conditions))
                    constructed_fun = add_variant_collection(res, promised_collections_funcs, is_sink)
                    return lambda run_id, iteration: constructed_fun(run_id, iteration),
                else:
                    if is_alternative and is_sink:
                        schemes = [scheme_info] * len(arg.group)
                    else:
                        if scheme_info is None:
                            schemes = [None] * len(arg.group)
                        else:
                            schemes = []
                            for subscheme in scheme_info:
                                if subscheme is not None and subscheme.endswith("*"):
                                    subscheme = subscheme[:-1] if len(subscheme) > 1 else None
                                    for _ in range(len(arg.group) - len(scheme_info) + 1):
                                        schemes.append((subscheme,))
                                else:
                                    schemes.append((subscheme,))
                            if len(arg.group) != len(schemes) and len(arg.group) == 1:
                                indices = arg.group[0].indices
                                if indices is not None and len(indices) == len(schemes):
                                    schemes = [schemes]
                            if len(arg.group) != len(schemes):
                                raise EntityException(f"wrong group subarguments size for argument with name={name} in processor with id={bind_id}: expected {len(schemes)} ({schemes}), found {len(arg.group)} ({arg.group})")
                    res = []
                    for i, (subarg, scheme) in enumerate(zip(arg.group, schemes)):
                        if key is not None:
                            key = (*key[0:3], i)
                        res.append(arg_add(subarg, bind_id, name, scheme, loop=loop, key=key)[0])
                    return tuple(res)
            else:
                raise Exception("wrong arguments structure")

        bind_id_to_cluster_num = -1
        for bind_id, entity in pipeline.processors.items():     # TODO set also loopArguments, loopConditions
            schemes_info, ret_type, sink_name = self.__registry.get_schemes_info(entity.processorId, EntityType.PROCESSOR)
            if schemes_info is None:
                raise EntityException(f"not exist schemes info for {entity.processorId}")
            if self.__is_local:
                bind_ids_list.append(bind_id)
                bind_id_to_cluster[bind_id] = bind_id_to_cluster_num
                bind_id_to_cluster_num -= 1

            collections_template: List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]] = []
            loop_collections_template: List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]] = []

            with_context = False
            for name, (f, scheme_info) in schemes_info.items():
                if scheme_info == C.CONTEXT:
                    with_context = True
                    if name in entity.arguments:
                        self.__logs_buffer.write(f"warn: try set argument with name={name} in processor with id={bind_id} - Context argument cannot be set\n")
                    if entity.loopArguments is not None and name in entity.loopArguments:
                        self.__logs_buffer.write(f"warn: try set loop argument with name={name} in processor with id={bind_id} - Context argument cannot be set\n")
                    continue

                arg = entity.arguments.get(name)
                if arg is None:
                    raise EntityException(f"argument with name={name} not exist in processors with id={bind_id}")
                if name == sink_name:
                    if arg.group is not None:
                        colls_template = []
                        for subarg in arg.group:
                            colls_template.append(arg_add(subarg, bind_id, name, scheme_info, first=True))
                        collections_template.append((colls_template, f, scheme_info))
                    elif arg.alternative is not None:
                        collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, is_sink=True), f, scheme_info))
                    else:
                        collections_template.append(([arg_add(arg, bind_id, name, scheme_info, first=True)], f, scheme_info))
                else:
                    collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True), f, scheme_info))

                # loop
                if entity.loopArguments is not None:
                    arg = entity.loopArguments.get(name)
                    if arg is None:
                        raise EntityException(f"loop argument with name={name} not exist in processors with id={bind_id}")
                    if name == sink_name:
                        if arg.group is not None:
                            colls_template = []
                            for subarg in arg.group:
                                colls_template.append(arg_add(subarg, bind_id, name, scheme_info, first=True, loop=True))
                            loop_collections_template.append((colls_template, f, scheme_info))
                        elif arg.alternative is not None:
                            loop_collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, loop=True, is_sink=True), f, scheme_info))
                        else:
                            loop_collections_template.append(([arg_add(arg, bind_id, name, scheme_info, first=True, loop=True)], f, scheme_info))
                    else:
                        loop_collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, loop=True), f, scheme_info))

            if len(schemes_info) != len(entity.arguments) + with_context:
                for name in entity.arguments:
                    if name not in schemes_info:
                        self.__logs_buffer.write(f"warn: unused argument with name={name} in processor with id={bind_id}\n")
            if entity.loopArguments is not None and len(schemes_info) != len(entity.loopArguments) + with_context:
                for name in entity.loopArguments:
                    if name not in schemes_info:
                        self.__logs_buffer.write(f"warn: unused argument with name={name} in processor with id={bind_id} (loop)\n")

            if entity.conditions is not None:
                bind_id_to_num_conds: Dict[str, List[Tuple[int, bool]]] = {}
                for i, conds in enumerate(entity.conditions):
                    for cond_bind_id, cond_value in conds.items():
                        num_conds = bind_id_to_num_conds.get(cond_bind_id)
                        if num_conds is None:
                            num_conds = []
                            bind_id_to_num_conds[cond_bind_id] = num_conds
                        num_conds.append((i, cond_value))

                if len(bind_id_to_num_conds) > 0:
                    for cond_bind_id, num_conds in bind_id_to_num_conds.items():
                        next = self.__nexts_conds.get(cond_bind_id)
                        if next is None:
                            next = {}
                            self.__nexts_conds[cond_bind_id] = next
                        next[bind_id] = num_conds

                    self.__wait_bind_ids_conds[bind_id] = entity.conditions

            if entity.loopConditions is not None:
                bind_id_to_num_conds: Dict[str, List[Tuple[int, bool]]] = {}
                for i, conds in enumerate(entity.loopConditions):
                    for cond_bind_id, cond_value in conds.items():
                        num_conds = bind_id_to_num_conds.get(cond_bind_id)
                        if num_conds is None:
                            num_conds = []
                            bind_id_to_num_conds[cond_bind_id] = num_conds
                        num_conds.append((i, cond_value))

                if len(bind_id_to_num_conds) > 0:
                    if self.__is_local:
                        cur_loop_order_deps = loop_order_deps.get(bind_id)
                        if cur_loop_order_deps is None:
                            cur_loop_order_deps = set()
                            loop_order_deps[bind_id] = cur_loop_order_deps

                        for cond_bind_id in bind_id_to_num_conds.keys():
                            cur_loop_order_deps.add(cond_bind_id)

                    for cond_bind_id, num_conds in bind_id_to_num_conds.items():
                        next = self.__loop_nexts_conds.get(cond_bind_id)
                        if next is None:
                            next = {}
                            self.__loop_nexts_conds[cond_bind_id] = next
                        next[bind_id] = num_conds

                    loop_wait_bind_ids_conds[bind_id] = entity.loopConditions

            pipeline_app = PipelineApp(
                processorId=entity.processorId,
                outputId=entity.outputId,
                image=self.__init.image,
            )
            app_cfg = get_app_cfg(entity.cfg, self.__logs_buffer)
            japp = self.__registry.create_app(self.__init, bind_id, self.__common_cfg, pipeline_app, app_cfg, local_dfs=self.__collections_holder.local_dfs, index=self.__scale_index, scale=self.__scale[bind_id])
            japp.set_operation(EntityType.PROCESSOR)

            run_collections_template[bind_id] = collections_template
            loop_run_collections_template[bind_id] = loop_collections_template
            res[bind_id] = JuliusPipelineItem(japp, self.__hash)
        for bind_id, entity in pipeline.conditions.items():     # FIXME copypaste, TODO set also loopArguments
            schemes_info, ret_type, sink_name = self.__registry.get_schemes_info(entity.conditionId, EntityType.CONDITION)
            if schemes_info is None:
                raise EntityException(f"not exist schemes info for {entity.conditionId}")
            if self.__is_local:
                bind_ids_list.append(bind_id)
                bind_id_to_cluster[bind_id] = bind_id_to_cluster_num
                bind_id_to_cluster_num -= 1

            collections_template: List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]] = []
            loop_collections_template: List[Tuple[Union[Tuple[Callable[[str, int], Collection]], List[Tuple[Callable[[str, int], Collection]]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]] = []

            with_context = False
            for name, (f, scheme_info) in schemes_info.items():
                if scheme_info == C.CONTEXT:
                    with_context = True
                    if name in entity.arguments:
                        self.__logs_buffer.write(f"warn: try set argument with name={name} in condition with id={bind_id} - Context argument cannot be set\n")
                    if entity.loopArguments is not None and name in entity.loopArguments:
                        self.__logs_buffer.write(f"warn: try set loop argument with name={name} in processor with id={bind_id} - Context argument cannot be set\n")
                    continue

                arg = entity.arguments.get(name)
                if arg is None:
                    raise EntityException(f"argument with name={name} not exist in processors with id={bind_id}")
                if name == sink_name:
                    if arg.group is not None:
                        colls_template = []
                        for subarg in arg.group:
                            colls_template.append(arg_add(subarg, bind_id, name, scheme_info, first=True))
                        collections_template.append((colls_template, f, scheme_info))
                    elif arg.alternative is not None:
                        collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, is_sink=True), f, scheme_info))
                    else:
                        collections_template.append(([arg_add(arg, bind_id, name, scheme_info, first=True)], f, scheme_info))
                else:
                    collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True), f, scheme_info))

                # loop
                if entity.loopArguments is not None:
                    arg = entity.loopArguments.get(name)
                    if arg is None:
                        raise EntityException(f"loop argument with name={name} not exist in processors with id={bind_id}")
                    if name == sink_name:
                        if arg.group is not None:
                            colls_template = []
                            for subarg in arg.group:
                                colls_template.append(arg_add(subarg, bind_id, name, scheme_info, first=True, loop=True))
                            loop_collections_template.append((colls_template, f, scheme_info))
                        elif arg.alternative is not None:
                            loop_collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, loop=True, is_sink=True), f, scheme_info))
                        else:
                            loop_collections_template.append(([arg_add(arg, bind_id, name, scheme_info, first=True, loop=True)], f, scheme_info))
                    else:
                        loop_collections_template.append((arg_add(arg, bind_id, name, scheme_info, first=True, loop=True), f, scheme_info))

            if len(schemes_info) != len(entity.arguments) + with_context:
                for name in entity.arguments:
                    if name not in schemes_info:
                        self.__logs_buffer.write(f"warn: unused argument with name={name} in processor with id={bind_id}\n")
            if entity.loopArguments is not None and len(schemes_info) != len(entity.loopArguments) + with_context:
                for name in entity.loopArguments:
                    if name not in schemes_info:
                        self.__logs_buffer.write(f"warn: unused argument with name={name} in processor with id={bind_id} (loop)\n")

            if entity.conditions is not None:
                bind_id_to_num_conds: Dict[str, List[Tuple[int, bool]]] = {}
                for i, conds in enumerate(entity.conditions):
                    for cond_bind_id, cond_value in conds.items():
                        num_conds = bind_id_to_num_conds.get(cond_bind_id)
                        if num_conds is None:
                            num_conds = []
                            bind_id_to_num_conds[cond_bind_id] = num_conds
                        num_conds.append((i, cond_value))

                if len(bind_id_to_num_conds) > 0:
                    for cond_bind_id, num_conds in bind_id_to_num_conds.items():
                        next = self.__nexts_conds.get(cond_bind_id)
                        if next is None:
                            next = {}
                            self.__nexts_conds[cond_bind_id] = next
                        next[bind_id] = num_conds

                    self.__wait_bind_ids_conds[bind_id] = entity.conditions

            if entity.loopConditions is not None:
                bind_id_to_num_conds: Dict[str, List[Tuple[int, bool]]] = {}
                for i, conds in enumerate(entity.loopConditions):
                    for cond_bind_id, cond_value in conds.items():
                        num_conds = bind_id_to_num_conds.get(cond_bind_id)
                        if num_conds is None:
                            num_conds = []
                            bind_id_to_num_conds[cond_bind_id] = num_conds
                        num_conds.append((i, cond_value))

                if len(bind_id_to_num_conds) > 0:
                    if self.__is_local:
                        cur_loop_order_deps = loop_order_deps.get(bind_id)
                        if cur_loop_order_deps is None:
                            cur_loop_order_deps = set()
                            loop_order_deps[bind_id] = cur_loop_order_deps

                        for cond_bind_id in bind_id_to_num_conds.keys():
                            cur_loop_order_deps.add(cond_bind_id)

                    for cond_bind_id, num_conds in bind_id_to_num_conds.items():
                        next = self.__loop_nexts_conds.get(cond_bind_id)
                        if next is None:
                            next = {}
                            self.__loop_nexts_conds[cond_bind_id] = next
                        next[bind_id] = num_conds

                    loop_wait_bind_ids_conds[bind_id] = entity.loopConditions

            pipeline_app = PipelineApp(
                conditionId=entity.conditionId,
                image=self.__init.image,
            )

            app_cfg = get_app_cfg(entity.cfg, self.__logs_buffer)
            japp = self.__registry.create_app(self.__init, bind_id, self.__common_cfg, pipeline_app, app_cfg, local_dfs=self.__collections_holder.local_dfs, index=self.__scale_index, scale=self.__scale[bind_id])     # TODO set task_id
            japp.set_operation(EntityType.CONDITION)

            run_collections_template[bind_id] = collections_template
            loop_run_collections_template[bind_id] = loop_collections_template
            res[bind_id] = JuliusPipelineItem(japp, self.__hash)

        if self.__is_local:
            self.__bind_ids_list = bind_ids_list

            for bind_id, deps in loop_wait_bind_ids.items():
                cur_loop_order_deps = loop_order_deps.get(bind_id)
                if cur_loop_order_deps is None:
                    cur_loop_order_deps = set()
                    loop_order_deps[bind_id] = cur_loop_order_deps

                for dep_bind_id in deps.keys():
                    cur_loop_order_deps.add(dep_bind_id)
            self.__init.loopOrderDeps = loop_order_deps
            self.__init.alternativeLoopOrderDeps = alt_loop_order_deps
            self.__init.pipeline.bindIdToCluster = bind_id_to_cluster

            all_loop_next_bind_ids = full_next_bind_ids(self.__loop_nexts, self.__loop_nexts_conds, self.__alt_loop_nexts)
            clusters = find_clusters(bind_id_to_cluster, all_loop_next_bind_ids)
            clusters = fix_clusters(clusters, bind_id_to_cluster)
            self.__init.clusters = clusters

            if len(self.__loop_nexts) > 0 or len(self.__alt_loop_nexts) > 0 or len(self.__loop_nexts_conds) > 0:
                all_next_bind_ids = full_next_bind_ids(self.__nexts, self.__nexts_conds, self.__alt_nexts)
                all_wait_bind_ids = full_wait_bind_ids(self.__wait_bind_ids, self.__wait_bind_ids_conds, self.__alt_wait_bind_ids)
                self.__init.loopIterationIncrement = start_loop_bind_ids(bind_id_to_cluster, all_next_bind_ids, all_wait_bind_ids, all_loop_next_bind_ids, clusters)

        if len(self.__init.clusters) > 0:
            for bind_id, indices in self.__init.clusters.items():
                bind_id_wait_bind_ids = loop_wait_bind_ids.get(bind_id)
                for i in indices:
                    cur_wait_bind_ids = self.__cluster_wait_bind_ids.get(i)
                    if cur_wait_bind_ids is None:
                        cur_wait_bind_ids = {}
                        self.__cluster_wait_bind_ids[i] = cur_wait_bind_ids
                    if bind_id_wait_bind_ids is not None:
                        cur_wait_bind_ids[bind_id] = bind_id_wait_bind_ids

                bind_id_wait_bind_ids_conds = loop_wait_bind_ids_conds.get(bind_id)
                for i in indices:
                    cur_wait_bind_ids = self.__cluster_wait_bind_ids_conds.get(i)
                    if cur_wait_bind_ids is None:
                        cur_wait_bind_ids = {}
                        self.__cluster_wait_bind_ids_conds[i] = cur_wait_bind_ids
                    if bind_id_wait_bind_ids_conds is not None:
                        cur_wait_bind_ids[bind_id] = bind_id_wait_bind_ids_conds

                alt_bind_id_wait_bind_ids = alt_loop_wait_bind_ids.get(bind_id)
                for i in indices:
                    cur_wait_bind_ids = self.__alt_cluster_wait_bind_ids.get(i)
                    if cur_wait_bind_ids is None:
                        cur_wait_bind_ids = {}
                        self.__alt_cluster_wait_bind_ids[i] = cur_wait_bind_ids
                    if alt_bind_id_wait_bind_ids is not None:
                        cur_wait_bind_ids[bind_id] = alt_bind_id_wait_bind_ids
            for i, bind_id in enumerate(self.__bind_ids_list):
                bind_id_wait_bind_ids = loop_wait_bind_ids.get(bind_id)
                if bind_id_wait_bind_ids is None:           # cluster_from = -i-1
                    self.__cluster_wait_bind_ids[-i-1] = {}
                else:
                    self.__cluster_wait_bind_ids[-i-1] = {bind_id: bind_id_wait_bind_ids}

                bind_id_wait_bind_ids_conds = loop_wait_bind_ids_conds.get(bind_id)
                if bind_id_wait_bind_ids_conds is None:     # cluster_from = -i-1
                    self.__cluster_wait_bind_ids_conds[-i-1] = {}
                else:
                    self.__cluster_wait_bind_ids_conds[-i-1] = {bind_id: bind_id_wait_bind_ids_conds}

                alt_bind_id_wait_bind_ids = alt_loop_wait_bind_ids.get(bind_id)
                if alt_bind_id_wait_bind_ids is None:       # cluster_from = -i-1
                    self.__alt_cluster_wait_bind_ids[-i-1] = {}
                else:
                    self.__alt_cluster_wait_bind_ids[-i-1] = {bind_id: alt_bind_id_wait_bind_ids}
        return res

    def __set_collections(self, run_id: str, iteration: int):
        def create_collections(argument_fun: Union[Callable[[str, int], Collection], Tuple[Callable[[str, int], Collection], ...]]) -> Union[Collection, Tuple[Collection, ...]]:
            if isinstance(argument_fun, Tuple):
                res = []
                for subargument_fun in argument_fun:
                    res.append(create_collections(subargument_fun))
                return tuple(res)
            else:
                return argument_fun(run_id, iteration)

        run_collections = self.__run_collections.get(run_id)
        if run_collections is None:
            run_collections = {}
            self.__run_collections[run_id] = run_collections

        run_iter_collections_template = self.__run_collections_template if iteration == 0 else self.__loop_run_collections_template
        for bind_id, run_collections_template in run_iter_collections_template.items():
            collections: List[Tuple[Union[Tuple[Collection, ...], List[Tuple[Collection, ...]]], Callable[[VarArg(pd.DataFrame)], JDF], Optional[Tuple[Optional[str], ...]]]] = []

            for collections_template, f, scheme_info in run_collections_template:
                if isinstance(collections_template, List):
                    res = []
                    for subarg_collections_template in collections_template:
                        assert isinstance(subarg_collections_template, Tuple), f"internal error: {subarg_collections_template}"
                        res.append(create_collections(subarg_collections_template))
                else:
                    assert isinstance(collections_template, Tuple), f"internal error: {collections_template}"
                    res = create_collections(collections_template)
                collections.append((res, f, scheme_info))

            iter_to_collections = run_collections.get(bind_id)
            if iter_to_collections is None:
                iter_to_collections = {}
                run_collections[bind_id] = iter_to_collections
            iter_to_collections[iteration] = collections

    def __set_collections_for_iteration(self, run_id: str, iteration: int):
        set_collections_next_iteration = self.__set_collections_next_iteration_by_run_id.get(run_id, 0)
        if set_collections_next_iteration <= iteration:
            while set_collections_next_iteration <= iteration:
                self.__set_collections(run_id, set_collections_next_iteration)
                set_collections_next_iteration += 1
            self.__set_collections_next_iteration_by_run_id[run_id] = set_collections_next_iteration

    def __local_log(self, run_id: str, bind_id: str, iteration: int, log: str):
        if self.__is_local:
            if self.__scaled:
                self.__logs_buffer.write(f"{log} | id={bind_id}, iter={iteration}, index={self.__scale_index}, run={run_id}\n")
            else:
                self.__logs_buffer.write(f"{log} | id={bind_id}, iter={iteration}, run={run_id}\n")

    async def __run_fail(self, julius_app, run_id: str, bind_id: str, iteration: int, is_processor: bool, trace: str, err_type: str, err_args: List[str], is_malevich_err: bool, collections: List[List[Union[LocalCollection, ObjectCollection, CompositeCollection, List[Union[LocalCollection, ObjectCollection, CompositeCollection]]]]]):
        struct = None
        if self.__fail_storage is not None:
            try:
                struct = self.__fail_storage.save(julius_app, self.__init.operationId, run_id, bind_id, iteration, is_processor, trace, err_type, err_args, is_malevich_err, julius_app._cfg_dict_if_need(), collections)
            except:
                self.__logs_buffer.write(f"save to fail storage fail\n")
                self.__logs_buffer.write(f"{traceback.format_exc()}\n")
        if not C.IS_LOCAL and C.WS is None:  # TODO allow for ws
            if struct is None:
                struct = fail_structure(julius_app, self.__init.operationId, run_id, bind_id, iteration, is_processor, trace, err_type, err_args, is_malevich_err, julius_app._cfg_dict_if_need())
            await post_error_info(struct, self.__logs_buffer)

    async def __save_collections(self, colls: List[Collection], pipeline_item: JuliusPipelineItem, bind_id: str, *, save_force: bool = False):
        saves = []  # save needed
        to_save = self.__init.pipeline.results.get(bind_id)
        if to_save is not None:
            for save_res in to_save:
                if save_res.index is None:
                    for i, result in enumerate(colls):
                        saves.append(save_real_collection(result, pipeline_item.japp, save_res.name, index=i, group_name=save_res.name, save_force=save_force))
                else:
                    i = save_res.index
                    if i < len(colls):
                        saves.append(save_real_collection(colls[i], pipeline_item.japp, save_res.name, index=i, group_name=save_res.name, save_force=save_force))
                    else:
                        pipeline_item.japp.logs_buffer.write(f"not save {save_res.name} - results size={len(colls)}, index={i}\n")
        await asyncio.gather(*saves)

    async def __run(self, run_id: str, iteration: int, items: Dict[str, JuliusPipelineItem], bind_id: str) -> bool:
        self.__local_log(run_id, bind_id, iteration, "run")

        pipeline_item = items.get(bind_id)
        if pipeline_item is None:
            return True     # not exist in current app

        collections = self.__run_collections.get(run_id, {}).get(bind_id, {}).get(iteration)
        if collections is None:
            raise EntityException(f"internal error: collections not set before run bind_id={bind_id}")

        is_true = None
        if pipeline_item.japp.get_operation() == EntityType.CONDITION:
            try:
                args, interpret_colls = await self.__collections_holder.interpret(pipeline_item.japp, collections, pipeline_item.japp.get_cfg())
            except BaseException as ex:
                if run_id in self.__run_items:
                    await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, False, PipelineStructureUpdate(), branch=False, hash=pipeline_item.hash)
                raise ex

            ok, is_true = await pipeline_item.run_condition(args)
            if not ok:  # is_true - traceback and other error info
                self.__local_log(run_id, bind_id, iteration, "fail")
                if run_id in self.__run_items:
                    await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, ok, PipelineStructureUpdate(), branch=True, hash=pipeline_item.hash)
                    trace, err_type, err_args, is_malevich_err = is_true
                    await self.__run_fail(pipeline_item.japp, run_id, bind_id, iteration, False, trace, err_type, err_args, is_malevich_err, interpret_colls)
                return ok
            self.__local_log(run_id, bind_id, iteration, f"done ({is_true})")

            if self.__scale[bind_id] == 1:
                tasks, struct_update = self.__run_next(run_id, iteration, items, bind_id, is_true)
                self.__collections_holder.conds(run_id, iteration, {bind_id: is_true})
            else:
                tasks, struct_update = [], StructureUpdate()
            if run_id in self.__run_items:
                await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, ok, struct_update.to_scheme(), branch=is_true, hash=pipeline_item.hash)
        else:  # processor
            try:
                args, interpret_colls = await self.__collections_holder.interpret(pipeline_item.japp, collections, pipeline_item.japp.get_cfg())
            except BaseException as ex:
                if run_id in self.__run_items:
                    await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, False, PipelineStructureUpdate(), hash=pipeline_item.hash)
                raise ex

            ok, colls = await pipeline_item.run_processor(args)
            if not ok:  # colls - traceback and other error info
                self.__local_log(run_id, bind_id, iteration, "fail")
                if run_id in self.__run_items:
                    await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, ok, PipelineStructureUpdate(), hash=pipeline_item.hash)
                    trace, err_type, err_args, is_malevich_err = colls
                    await self.__run_fail(pipeline_item.japp, run_id, bind_id, iteration, True, trace, err_type, err_args, is_malevich_err, interpret_colls)
                return ok
            self.__local_log(run_id, bind_id, iteration, "done")

            if pipeline_item.japp.is_stream():
                streams_by_bind_id = self.__run_stream_res.get(run_id)
                if streams_by_bind_id is None:
                    streams_by_bind_id = {}
                    self.__run_stream_res[run_id] = streams_by_bind_id
                if streams_by_bind_id.get(bind_id) is not None:
                    self.__logs_buffer.write(f"stream already exist, bind_id = {bind_id}\n")
                else:
                    streams_by_bind_id[bind_id] = colls
                tasks, struct_update = [], StructureUpdate()
            else:
                if self.__scale[bind_id] == 1:
                    await self.__save_collections(colls, pipeline_item, bind_id)

                    tasks, struct_update = self.__run_next(run_id, iteration, items, bind_id, is_true)
                    self.__collections_holder.done(run_id, bind_id, iteration, colls)
                    self.__collections_holder.conds(run_id, iteration, {bind_id: True})
                else:
                    tasks, struct_update = [], StructureUpdate()
            if run_id in self.__run_items:
                await self.__tracker.finished(self.__init.operationId, run_id, bind_id, iteration, True, struct_update.to_scheme(), colls=[] if pipeline_item.japp.is_stream() else colls, hash=pipeline_item.hash)

        if len(tasks) > 0:
            return all(await gather(*tasks))
        else:
            return True

    def __prepare_next_collections(self, collections_binds_funcs: Dict[Tuple[str, int], Dict[str, List[Callable[[int], None]]]], next_pair: Tuple[str, int], bind_id: str, iteration: int):
        funcs = collections_binds_funcs.get(next_pair, {}).get(bind_id)
        if funcs is not None:
            for f in funcs:
                f(iteration)
            funcs.clear()

    def __run_next(self, run_id: str, iteration: int, items: Dict[str, JuliusPipelineItem], bind_id: str, cond_value: Optional[bool], with_update: bool = True, runned: bool = True, *, struct_update: Optional[StructureUpdate] = None) -> Tuple[List[Coroutine[Any, Any, bool]], StructureUpdate]:
        is_processor = bind_id in self.__processor_bind_ids

        if not runned and is_processor:
            self.__collections_holder.conds(run_id, iteration, {bind_id: False})
        if is_processor and cond_value == False:
            runned = False

        # self.__logs_buffer.write(f"run_next {bind_id} {iteration} {cond_value} {runned}\n")

        tasks = []
        if struct_update is None:
            struct_update = StructureUpdate()

        if not runned and not is_processor:
            return tasks, struct_update

        run_next_tasks = []

        run_wait_bind_ids = self.__run_wait_bind_ids[run_id]
        run_wait_bind_ids_conds = self.__run_wait_bind_ids_conds[run_id]
        run_alt_wait_bind_ids = self.__run_alt_wait_bind_ids[run_id]
        loop_structures = self.__run_loop_structures[run_id]

        zero_iteration = loop_structures.zero_iteration_mapping.get(bind_id)
        if runned:
            if zero_iteration is None:
                zero_iteration = 0
                loop_structures.zero_iteration_mapping[bind_id] = zero_iteration
                struct_update.zero_iteration_mapping[bind_id] = zero_iteration
            is_zero_iteration = zero_iteration == iteration
        else:
            is_zero_iteration = zero_iteration is None or zero_iteration == iteration

        if is_zero_iteration:   # update for alternative another choice
            if runned:
                loop_structures.not_runned_bind_ids.discard(bind_id)

            for next_bind_id in self.__nexts.get(bind_id, []):
                if next_bind_id not in loop_structures.not_runned_bind_ids:
                    is_zero_iteration = False
                    break

            # TODO understand when it is necessary and problems
            if is_zero_iteration:
                for next_bind_id in self.__nexts_conds.get(bind_id, []):
                    if next_bind_id not in loop_structures.not_runned_bind_ids:
                        is_zero_iteration = False
                        break

            if is_zero_iteration:
                for next_bind_id in self.__alt_nexts.get(bind_id, []):
                    if next_bind_id not in loop_structures.not_runned_bind_ids:
                        is_zero_iteration = False
                        break

        # self.__logs_buffer.write(f"loop_structures.iterations_connection before {loop_structures.iterations_connection} | {loop_structures.iterations_transition}\n")

        if is_zero_iteration:
            next_bind_id_iteration = 0  # FIXME mb wrong iteration?

            nexts = self.__nexts.get(bind_id, set())
            if runned:
                for next_bind_id in nexts:
                    wait_bind_ids = run_wait_bind_ids[next_bind_id]
                    if wait_bind_ids is None:
                        continue

                    wait_bind_id_res = wait_bind_ids[bind_id]
                    if wait_bind_id_res is None or wait_bind_id_res == cond_value or (cond_value is None and wait_bind_id_res):
                        wait_bind_ids.pop(bind_id)
                        if is_processor:
                            self.__prepare_next_collections(loop_structures.collections_binds_funcs, (next_bind_id, next_bind_id_iteration), bind_id, iteration)
                        if len(wait_bind_ids) == 0:
                            run_wait_bind_ids.pop(next_bind_id)
                            if next_bind_id not in run_alt_wait_bind_ids and next_bind_id not in run_wait_bind_ids_conds:
                                loop_structures.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                                struct_update.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                                self.__set_collections_for_iteration(run_id, next_bind_id_iteration + 1)
                                tasks.append(self.__run(run_id, next_bind_id_iteration, items, next_bind_id))
                    else:
                        run_wait_bind_ids[next_bind_id] = None
                        next_bind_id_copy = next_bind_id
                        run_next_tasks.append(lambda: self.__run_next(run_id, next_bind_id_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))
            nexts_conds = self.__nexts_conds.get(bind_id, {})
            for next_bind_id, num_conds in nexts_conds.items():
                wait_bind_ids_conds = run_wait_bind_ids_conds.get(next_bind_id)
                changed_next_conds = False
                if wait_bind_ids_conds is not None:
                    for num, cond in num_conds:
                        num_next_wait_bind_ids_conds = wait_bind_ids_conds[num]
                        if num_next_wait_bind_ids_conds is None:
                            continue

                        if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or\
                                (not runned and cond == False):
                            if bind_id not in num_next_wait_bind_ids_conds:
                                continue

                            num_next_wait_bind_ids_conds.pop(bind_id)
                            if len(num_next_wait_bind_ids_conds) == 0:
                                run_wait_bind_ids_conds.pop(next_bind_id)
                                changed_next_conds = True
                        else:
                            wait_bind_ids_conds[num] = None
                            exist_suitable = False
                            for next_num_conds in wait_bind_ids_conds:
                                if next_num_conds is not None:
                                    exist_suitable = True
                                    break
                            if not exist_suitable:
                                run_wait_bind_ids_conds[next_bind_id] = None
                                next_bind_id_copy = next_bind_id
                                run_next_tasks.append(lambda: self.__run_next(run_id, next_bind_id_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                if next_bind_id not in run_wait_bind_ids and next_bind_id not in run_alt_wait_bind_ids and changed_next_conds:
                    loop_structures.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                    struct_update.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                    self.__set_collections_for_iteration(run_id, next_bind_id_iteration + 1)
                    tasks.append(self.__run(run_id, next_bind_id_iteration, items, next_bind_id))
            for next_bind_id, name_to_num_conds in self.__alt_nexts.get(bind_id, {}).items():
                alt_wait_bind_ids = run_alt_wait_bind_ids.get(next_bind_id)

                changed_alt_next = False
                if alt_wait_bind_ids is not None:
                    for name, num_conds in name_to_num_conds.items():
                        next_alt_wait_bind_ids = alt_wait_bind_ids[name]
                        for num, cond in num_conds:
                            num_next_alt_wait_bind_ids = next_alt_wait_bind_ids[num]
                            if num_next_alt_wait_bind_ids is None:
                                continue

                            if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or \
                                    (not runned and cond == False):
                                if is_processor:
                                    alt_dep_key = (run_id, next_bind_id, next_bind_id_iteration, name, num)
                                    deps = self.__alt_deps.get(alt_dep_key)
                                    if deps is None:
                                        deps = {}
                                        self.__alt_deps[alt_dep_key] = deps

                                    if bind_id not in deps:
                                        self.__prepare_next_collections(loop_structures.collections_binds_funcs,(next_bind_id, next_bind_id_iteration), bind_id, iteration)
                                        deps[bind_id] = iteration

                                if bind_id not in num_next_alt_wait_bind_ids:
                                    continue

                                num_next_alt_wait_bind_ids.pop(bind_id)
                                if len(num_next_alt_wait_bind_ids) == 0:
                                    if alt_wait_bind_ids.pop(name, None) is None:
                                        raise EntityException(f"several alternative arguments are suitable for name={name} in {next_bind_id}")
                                    if len(alt_wait_bind_ids) == 0:
                                        run_alt_wait_bind_ids.pop(next_bind_id)
                                        changed_alt_next = True
                            else:
                                next_alt_wait_bind_ids[num] = None
                                exist_suitable = False
                                for next_num_conds in next_alt_wait_bind_ids:
                                    if next_num_conds is not None:
                                        exist_suitable = True
                                        break
                                if not exist_suitable:
                                    run_alt_wait_bind_ids[next_bind_id] = None
                                    next_bind_id_copy = next_bind_id
                                    run_next_tasks.append(lambda: self.__run_next(run_id, next_bind_id_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                if next_bind_id not in run_wait_bind_ids and changed_alt_next and next_bind_id not in run_wait_bind_ids_conds:
                    loop_structures.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                    struct_update.zero_iteration_mapping[next_bind_id] = next_bind_id_iteration
                    self.__set_collections_for_iteration(run_id, next_bind_id_iteration + 1)
                    tasks.append(self.__run(run_id, next_bind_id_iteration, items, next_bind_id))

        iteration_increment_ids = self.__init.loopIterationIncrement.get(bind_id)
        exist_increment_ids = iteration_increment_ids is not None
        if not exist_increment_ids and not is_zero_iteration:
            exist_increment_ids = True
            iteration_increment_ids = {}

        if exist_increment_ids:
            iter_pair = (self.__init.pipeline.bindIdToCluster[bind_id], iteration)
            base_clusters = self.__init.clusters.get(bind_id, set())

            base_iterations_connect_wrapper = loop_structures.iterations_connection.get(iter_pair)
            if base_iterations_connect_wrapper is None:
                base_iterations_connect_dict = {iter_pair[0]: iter_pair[1]}
                struct_update.iterations_connection = {iter_pair: base_iterations_connect_dict.copy()}
                base_iterations_connect_wrapper = DictWrapper(loop_structures.dict_wrapper_index, base_iterations_connect_dict)
                loop_structures.iterations_connection[iter_pair] = base_iterations_connect_wrapper
                loop_structures.dict_wrapper_index += 1
            else:
                base_iterations_connect_dict = base_iterations_connect_wrapper.data
                struct_update.iterations_connection = {iter_pair: {}}

            alt_loop_nexts = self.__alt_loop_nexts.get(bind_id, {})
            all_nexts = copy.deepcopy(alt_loop_nexts)
            loop_nexts = self.__loop_nexts.get(bind_id, {})
            for next_bind_id in loop_nexts:
                if next_bind_id not in all_nexts:
                    all_nexts[next_bind_id] = None
            loop_nexts_conds = self.__loop_nexts_conds.get(bind_id, {})
            for next_bind_id, num_conds in loop_nexts_conds.items():
                cur_nexts = all_nexts.get(next_bind_id)
                if cur_nexts is None:
                    all_nexts[next_bind_id] = {_condition_key: num_conds}
                else:
                    cur_nexts[_condition_key] = num_conds
            for next_bind_id, name_to_num_conds in all_nexts.items():
                is_alternative = next_bind_id in alt_loop_nexts
                is_plain = next_bind_id in loop_nexts
                is_condition = next_bind_id in loop_nexts_conds

                increment_iteration = next_bind_id in iteration_increment_ids
                if is_zero_iteration and not increment_iteration:
                    continue

                if with_update:
                    if is_zero_iteration:
                        if len(base_iterations_connect_dict) == 1:
                            clusters = base_clusters.copy()

                            loop_order_deps = self.__init.loopOrderDeps.get(next_bind_id, set())
                            if (is_plain and runned) or is_condition:
                                for dep_bind_id in loop_order_deps:
                                    if dep_bind_id == bind_id:
                                        continue

                                    dep_iteration_increment_ids = self.__init.loopIterationIncrement.get(dep_bind_id)
                                    if dep_iteration_increment_ids is not None and next_bind_id in dep_iteration_increment_ids:
                                        index = self.__init.pipeline.bindIdToCluster[dep_bind_id]
                                        loop_structures.iterations_connection[(index, 0)] = base_iterations_connect_wrapper

                                        if index not in base_iterations_connect_dict:
                                            base_iterations_connect_dict[index] = 0
                                            struct_update.iterations_connection[iter_pair][index] = 0
                                        for index in self.__init.clusters.get(dep_bind_id, []):
                                            clusters.add(index)

                            if is_alternative:
                                for dep_bind_id in self.__init.alternativeLoopOrderDeps.get(next_bind_id, set()):
                                    if dep_bind_id in loop_order_deps or dep_bind_id == bind_id:
                                        continue

                                    dep_iteration_increment_ids = self.__init.loopIterationIncrement.get(dep_bind_id)
                                    if dep_iteration_increment_ids is not None and next_bind_id in dep_iteration_increment_ids:
                                        index = self.__init.pipeline.bindIdToCluster[dep_bind_id]
                                        loop_structures.iterations_connection[
                                            (index, 0)] = base_iterations_connect_wrapper

                                        if index not in base_iterations_connect_dict:
                                            base_iterations_connect_dict[index] = 0
                                            struct_update.iterations_connection[iter_pair][index] = 0
                                        for index in self.__init.clusters.get(dep_bind_id, []):
                                            clusters.add(index)

                            dicts: Set[DictWrapper[Dict[int, int]]] = set()
                            for cluster_index in clusters:
                                iterations_connection_wrapper = loop_structures.iterations_connection.get((cluster_index, 0))
                                if iterations_connection_wrapper is not None:
                                    dicts.add(iterations_connection_wrapper)

                            if len(dicts) == 1:
                                for iterations_connection_wrapper in dicts:
                                    for index, conn_iteration in iterations_connection_wrapper.items():
                                        if index not in base_iterations_connect_dict:
                                            struct_update.iterations_connection[iter_pair][index] = conn_iteration
                                    for index, conn_iteration in base_iterations_connect_dict.items():
                                        iterations_connection_wrapper[index] = conn_iteration
                                    base_iterations_connect_dict = iterations_connection_wrapper.data
                            elif len(dicts) > 1:
                                for iterations_connection_wrapper in dicts:
                                    for index, conn_iteration in iterations_connection_wrapper.items():
                                        if index not in base_iterations_connect_dict:
                                            base_iterations_connect_dict[index] = conn_iteration
                                            struct_update.iterations_connection[iter_pair][index] = conn_iteration
                                    iterations_connection_wrapper.data = base_iterations_connect_dict

                            for cluster_index in clusters:
                                if cluster_index not in base_iterations_connect_dict:
                                    cluster_iteration = 0
                                    if cluster_iteration != loop_structures.cluster_next_iteration[cluster_index]:
                                        raise EntityException(f"run_next: wrong iteration for {cluster_index}")
                                    loop_structures.iterations_connection[(cluster_index, cluster_iteration)] = base_iterations_connect_wrapper
                                    cluster_next_iteration = loop_structures.cluster_next_iteration[cluster_index] + 1
                                    loop_structures.cluster_next_iteration[cluster_index] = cluster_next_iteration
                                    struct_update.cluster_next_iteration[cluster_index] = cluster_next_iteration
                                    base_iterations_connect_dict[cluster_index] = cluster_iteration
                                    struct_update.iterations_connection[iter_pair][cluster_index] = cluster_iteration

                    next_bind_id_index = self.__init.pipeline.bindIdToCluster[next_bind_id]

                    next_bind_id_pair = None
                    pairs = set()

                    common_index = None
                    for next_index in self.__init.clusters.get(next_bind_id, []):
                        if next_index in base_clusters:
                            common_index = next_index

                            next_iteration = base_iterations_connect_dict.get(next_index)
                            if next_iteration is None:
                                next_iteration = loop_structures.cluster_next_iteration[next_index]
                                loop_structures.iterations_connection[(next_index, next_iteration)] = base_iterations_connect_wrapper
                                cluster_next_iteration = loop_structures.cluster_next_iteration[next_index] + 1
                                loop_structures.cluster_next_iteration[next_index] = cluster_next_iteration
                                struct_update.cluster_next_iteration[next_index] = cluster_next_iteration
                                base_iterations_connect_dict[next_index] = next_iteration
                                struct_update.iterations_connection[iter_pair][next_index] = next_iteration
                            elif increment_iteration:
                                next_iteration += 1
                            pairs.add((next_index, next_iteration))
                            break

                    add_next_bind_id_pair = True
                    if not increment_iteration:
                        next_bind_id_iteration = base_iterations_connect_dict.get(next_bind_id_index)
                        if next_bind_id_iteration is not None:
                            add_next_bind_id_pair = False
                            next_bind_id_pair = (next_bind_id_index, next_bind_id_iteration)
                            pairs.add(next_bind_id_pair)

                    iterations_transition_wrappers: Set[DictWrapper[Dict[int, int]]] = set()
                    if len(base_clusters) > 0:
                        for base_cluster_index in base_clusters:
                            if common_index == base_cluster_index:
                                continue

                            base_cluster_iteration = base_iterations_connect_dict[base_cluster_index]
                            base_pair = (base_cluster_index, base_cluster_iteration)

                            iterations_transition_wrappers_prev = loop_structures.iterations_transition_prev.get(base_pair)
                            if iterations_transition_wrappers_prev is not None:
                                for iterations_transition_wrapper in iterations_transition_wrappers_prev:
                                    iterations_transition_wrappers.add(iterations_transition_wrapper)
                            iterations_transition_wrapper = loop_structures.iterations_transition.get(base_pair)
                            if iterations_transition_wrapper is not None:
                                iterations_transition_wrappers.add(iterations_transition_wrapper)
                    # else:     # FIXME add else & check
                    iterations_transition_wrappers_prev = loop_structures.iterations_transition_prev.get(iter_pair)
                    if iterations_transition_wrappers_prev is not None:
                        for iterations_transition_wrapper in iterations_transition_wrappers_prev:
                            iterations_transition_wrappers.add(iterations_transition_wrapper)
                    iterations_transition_wrapper = loop_structures.iterations_transition.get(iter_pair)
                    if iterations_transition_wrapper is not None:
                        iterations_transition_wrappers.add(iterations_transition_wrapper)

                    for iterations_transition_wrapper in iterations_transition_wrappers:
                        if add_next_bind_id_pair:
                            next_iteration = iterations_transition_wrapper.get(next_bind_id_index)
                            if next_iteration is not None:
                                add_next_bind_id_pair = False
                                next_bind_id_pair = (next_bind_id_index, next_iteration)
                                pairs.add(next_bind_id_pair)

                        for next_index in self.__init.clusters.get(next_bind_id, []):
                            if next_index == common_index:
                                continue

                            next_iteration = iterations_transition_wrapper.get(next_index)
                            if next_iteration is not None:
                                pairs.add((next_index, next_iteration))

                    if add_next_bind_id_pair:
                        cluster_next_iteration = loop_structures.cluster_next_iteration[next_bind_id_index]
                        loop_structures.cluster_next_iteration[next_bind_id_index] = cluster_next_iteration + 1

                        struct_update.cluster_next_iteration[next_bind_id_index] = cluster_next_iteration + 1
                        next_bind_id_pair = (next_bind_id_index, cluster_next_iteration)
                        pairs.add(next_bind_id_pair)

                    #

                    dicts: Set[DictWrapper[Dict[int, int]]] = set()
                    for pair in pairs:
                        iterations_connection_wrapper = loop_structures.iterations_connection.get(pair)
                        if iterations_connection_wrapper is not None:
                            dicts.add(iterations_connection_wrapper)

                    iterations_connection_pairs = struct_update.iterations_connection.get(next_bind_id_pair)
                    if iterations_connection_pairs is None:
                        iterations_connection_pairs = {}
                        struct_update.iterations_connection[next_bind_id_pair] = iterations_connection_pairs
                    iterations_connection_wrapper = None
                    if len(dicts) == 0:
                        iterations_connection_wrapper = DictWrapper(loop_structures.dict_wrapper_index, {})
                        loop_structures.dict_wrapper_index += 1
                        for pair in pairs:
                            check(iterations_connection_wrapper, *pair)
                            iterations_connection_wrapper[pair[0]] = pair[1]
                            loop_structures.iterations_connection[pair] = iterations_connection_wrapper
                    elif len(dicts) == 1:
                        for iterations_connection_wrapper_i in dicts:     # one iteration
                            iterations_connection_wrapper = iterations_connection_wrapper_i
                            for pair in pairs:
                                check(iterations_connection_wrapper, *pair)
                                iterations_connection_wrapper[pair[0]] = pair[1]
                                loop_structures.iterations_connection[pair] = iterations_connection_wrapper
                    else:
                        iterations_connection_wrapper = None
                        for iterations_connection_wrapper_i in dicts:
                            if iterations_connection_wrapper is None:
                                iterations_connection_wrapper = iterations_connection_wrapper_i
                            else:
                                for index, conn_iteration in iterations_connection_wrapper_i.items():
                                    check(iterations_connection_wrapper, index, conn_iteration)
                                    iterations_connection_wrapper[index] = conn_iteration
                                iterations_connection_wrapper_i.data = iterations_connection_wrapper.data
                        for pair in pairs:
                            check(iterations_connection_wrapper, *pair)
                            if pair[0] not in iterations_connection_wrapper:
                                iterations_connection_wrapper[pair[0]] = pair[1]
                                loop_structures.iterations_connection[pair] = iterations_connection_wrapper

                    for next_index in self.__init.clusters.get(next_bind_id, []):
                        if next_index in iterations_connection_wrapper:
                            continue

                        next_iteration = loop_structures.cluster_next_iteration[next_index]
                        loop_structures.cluster_next_iteration[next_index] = next_iteration + 1
                        struct_update.cluster_next_iteration[next_index] = next_iteration + 1

                        loop_structures.iterations_connection[(next_index, next_iteration)] = iterations_connection_wrapper
                        check(iterations_connection_wrapper, next_index, next_iteration)
                        iterations_connection_wrapper[next_index] = next_iteration

                    iterations_connection_pairs.update(iterations_connection_wrapper)   # FIXME

                    #

                    dicts = set()
                    iterations_transition_used = False
                    iterations_transition: Dict[int, int] = {}
                    iterations_transition_wrapper_main: DictWrapper[Dict[int, int]] = None
                    if len(base_clusters) > 0:
                        for base_pair in base_iterations_connect_dict.items():
                            # if base_pair[0] < 0:
                            #     continue    # not cluster

                            iterations_transition_wrapper = loop_structures.iterations_transition.get(base_pair)
                            if iterations_transition_wrapper is not None:
                                dicts.add(iterations_transition_wrapper)
                            else:
                                iterations_transition_wrapper = DictWrapper(loop_structures.dict_wrapper_index, iterations_transition)
                                loop_structures.dict_wrapper_index += 1
                                loop_structures.iterations_transition[base_pair] = iterations_transition_wrapper
                                if not iterations_transition_used:
                                    dicts.add(iterations_transition_wrapper)
                                    iterations_transition_wrapper_main = iterations_transition_wrapper
                                    iterations_transition_used = True
                    else:
                        iterations_transition_wrapper = loop_structures.iterations_transition.get(iter_pair)
                        if iterations_transition_wrapper is not None:
                            dicts.add(iterations_transition_wrapper)
                        else:
                            iterations_transition_wrapper = DictWrapper(loop_structures.dict_wrapper_index, iterations_transition)
                            loop_structures.dict_wrapper_index += 1
                            loop_structures.iterations_transition[iter_pair] = iterations_transition_wrapper
                            if not iterations_transition_used:
                                dicts.add(iterations_transition_wrapper)
                                iterations_transition_wrapper_main = iterations_transition_wrapper
                                iterations_transition_used = True

                    if len(dicts) > 1:
                        for iterations_transition_wrapper in dicts:
                            if not iterations_transition_used:
                                iterations_transition = iterations_transition_wrapper.data
                                iterations_transition_wrapper_main = iterations_transition_wrapper
                                iterations_transition_used = True
                            elif iterations_transition_wrapper.data != iterations_transition:
                                for index, transition_iteration in iterations_transition_wrapper.items():
                                    iterations_transition[index] = transition_iteration

                                iterations_transition_wrapper.data = iterations_transition
                    elif len(dicts) == 1 and not iterations_transition_used:
                        for iterations_transition_wrapper in dicts:
                            iterations_transition = iterations_transition_wrapper.data
                            iterations_transition_wrapper_main = iterations_transition_wrapper
                            iterations_transition_used = True

                    if increment_iteration or next_bind_id not in self.__init.clusters:
                        for index, conn_iteration in iterations_connection_wrapper.items():
                            iterations_transition[index] = conn_iteration

                    struct_update.iterations_transition[iter_pair] = iterations_transition

                    prev_iter_transitions: Set[DictWrapper[Dict[int, int]]] = None
                    if next_bind_id in self.__init.clusters:
                        for pair in iterations_connection_wrapper.items():
                            # if pair[0] < 0:   # FIXME uncomment
                            #     continue  # not cluster

                            prev_iterations_transitions = loop_structures.iterations_transition_prev.get(pair)
                            if prev_iterations_transitions is not None:
                                if prev_iter_transitions is None:
                                    prev_iter_transitions = prev_iterations_transitions
                                elif prev_iter_transitions is not prev_iterations_transitions:
                                    prev_iter_transitions |= prev_iterations_transitions

                        if prev_iter_transitions is None:
                            prev_iter_transitions = set()
                        for pair in iterations_connection_wrapper.items():
                            # if pair[0] < 0:   # FIXME uncomment
                            #     continue  # not cluster

                            loop_structures.iterations_transition_prev[pair] = prev_iter_transitions
                    else:
                        prev_iter_transitions_next = loop_structures.iterations_transition_prev.get(next_bind_id_pair)
                        if prev_iter_transitions_next is not None:
                            prev_iter_transitions = prev_iter_transitions_next
                        else:
                            prev_iter_transitions = set()
                            loop_structures.iterations_transition_prev[next_bind_id_pair] = prev_iter_transitions

                    if iterations_transition_used and iterations_transition_wrapper_main not in prev_iter_transitions and not increment_iteration:
                        prev_iter_transitions.add(iterations_transition_wrapper_main)
                        if len(base_clusters) > 0:
                            for base_cluster_index in base_clusters:
                                base_cluster_iteration = base_iterations_connect_dict[base_cluster_index]
                                pair = (base_cluster_index, base_cluster_iteration)
                                break
                        else:
                            pair = iter_pair
                        iterations_transition_prev = loop_structures.iterations_transition_prev.get(pair)
                        if iterations_transition_prev is not None:
                            prev_iter_transitions |= iterations_transition_prev
                else:
                    next_bind_id_index = self.__init.pipeline.bindIdToCluster[next_bind_id]
                    next_bind_id_iteration = None if increment_iteration else base_iterations_connect_dict.get(next_bind_id_index)
                    if next_bind_id_iteration is None:
                        iterations_transition_wrapper = loop_structures.iterations_transition.get(iter_pair)
                        next_bind_id_iteration = iterations_transition_wrapper.get(next_bind_id_index)
                        if next_bind_id_iteration is None:
                            raise EntityException(f"internal error: can't recognize iteration: ({bind_id}, {iteration}) -> {next_bind_id}")
                    next_bind_id_pair = (next_bind_id_index, next_bind_id_iteration)
                    iterations_connection_wrapper = loop_structures.iterations_connection[next_bind_id_pair]

                if not runned and not is_alternative and not is_condition:
                    continue

                need_run = False
                clusters_indices_next = self.__init.clusters.get(next_bind_id, [])

                if len(clusters_indices_next) == 0:     # FIXME copypaste
                    next_index, next_iteration = next_bind_id_pair

                    changed = False

                    iter_to_app_wait_bind_ids = loop_structures.app_wait_bind_ids.get(next_index)
                    if iter_to_app_wait_bind_ids is None:
                        iter_to_app_wait_bind_ids = {}
                        loop_structures.app_wait_bind_ids[next_index] = iter_to_app_wait_bind_ids

                    app_wait_bind_ids: Dict[str, Dict[str, Optional[bool]]] = iter_to_app_wait_bind_ids.get(next_iteration)
                    if app_wait_bind_ids is None:
                        app_wait_bind_ids = copy.deepcopy(self.__cluster_wait_bind_ids[next_index])
                        iter_to_app_wait_bind_ids[next_iteration] = app_wait_bind_ids

                    wait_bind_ids = app_wait_bind_ids.get(next_bind_id)
                    need_run_plain = wait_bind_ids is None or len(wait_bind_ids) == 0

                    if runned and is_plain and wait_bind_ids is not None:
                        struct_update.count_app(next_index, next_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index])
                        wait_bind_id_res = wait_bind_ids[bind_id]
                        if wait_bind_id_res is None or wait_bind_id_res == cond_value or (cond_value is None and wait_bind_id_res):
                            wait_bind_ids.pop(bind_id)
                            changed = True
                            if is_processor:
                                self.__prepare_next_collections(loop_structures.collections_binds_funcs, (next_bind_id, next_iteration), bind_id, iteration)
                            if len(wait_bind_ids) == 0:
                                app_wait_bind_ids.pop(next_bind_id)
                                need_run_plain = True
                        else:
                            app_wait_bind_ids[next_bind_id] = None
                            next_bind_id_copy = next_bind_id
                            run_next_tasks.append(lambda: self.__run_next(run_id, next_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                    app_wait_bind_ids_conds: Dict[str, List[Dict[str, Optional[bool]]]] = None
                    if is_condition or next_bind_id in self.__cluster_wait_bind_ids_conds[next_index]:
                        iter_to_app_wait_bind_ids_conds = loop_structures.app_wait_bind_ids_conds.get(next_index)
                        if iter_to_app_wait_bind_ids_conds is None:
                            iter_to_app_wait_bind_ids_conds = {}
                            loop_structures.app_wait_bind_ids_conds[next_index] = iter_to_app_wait_bind_ids_conds

                        app_wait_bind_ids_conds = iter_to_app_wait_bind_ids_conds.get(next_iteration)
                        if app_wait_bind_ids_conds is None:
                            app_wait_bind_ids_conds = copy.deepcopy(self.__cluster_wait_bind_ids_conds[next_index])
                            iter_to_app_wait_bind_ids_conds[next_iteration] = app_wait_bind_ids_conds
                    exist_bind_ids_conds = app_wait_bind_ids_conds is not None and next_bind_id in app_wait_bind_ids_conds
                    if exist_bind_ids_conds:
                        changed = True

                    if is_condition:
                        wait_bind_ids_conds = app_wait_bind_ids_conds.get(next_bind_id)
                        if wait_bind_ids_conds is not None:
                            num_count: Dict[int, int] = {}
                            num_conds = name_to_num_conds[_condition_key]

                            for num, cond in num_conds:
                                num_next_wait_bind_ids_conds = wait_bind_ids_conds[num]
                                if num_next_wait_bind_ids_conds is None:
                                    continue

                                if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or \
                                        (not runned and cond == False):
                                    num_count[num] = 1
                                    if bind_id not in num_next_wait_bind_ids_conds:
                                        continue

                                    num_next_wait_bind_ids_conds.pop(bind_id)
                                    if len(num_next_wait_bind_ids_conds) == 0:
                                        app_wait_bind_ids_conds.pop(next_bind_id)
                                        exist_bind_ids_conds = False
                                else:
                                    num_count[num] = -1
                                    wait_bind_ids_conds[num] = None
                                    exist_suitable = False
                                    for next_num_conds in wait_bind_ids_conds:
                                        if next_num_conds is not None:
                                            exist_suitable = True
                                            break
                                    if not exist_suitable:
                                        app_wait_bind_ids_conds[next_bind_id] = None
                                        next_bind_id_copy = next_bind_id
                                        run_next_tasks.append(lambda: self.__run_next(run_id, next_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                                        struct_update.count_app(next_index, next_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], num_count={})
                                        num_count.clear()
                                        break

                            if len(num_count) > 0:
                                struct_update.count_app(next_index, next_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], num_count=num_count)

                    alt_app_wait_bind_ids: Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]] = None
                    if is_alternative or next_bind_id in self.__alt_cluster_wait_bind_ids[next_index]:
                        iter_to_alt_app_wait_bind_ids = loop_structures.alt_app_wait_bind_ids.get(next_index)
                        if iter_to_alt_app_wait_bind_ids is None:
                            iter_to_alt_app_wait_bind_ids = {}
                            loop_structures.alt_app_wait_bind_ids[next_index] = iter_to_alt_app_wait_bind_ids

                        alt_app_wait_bind_ids = iter_to_alt_app_wait_bind_ids.get(next_iteration)
                        if alt_app_wait_bind_ids is None:
                            alt_app_wait_bind_ids = copy.deepcopy(self.__alt_cluster_wait_bind_ids[next_index])
                            iter_to_alt_app_wait_bind_ids[next_iteration] = alt_app_wait_bind_ids
                    exist_alt_bind_ids = alt_app_wait_bind_ids is not None and next_bind_id in alt_app_wait_bind_ids
                    if exist_alt_bind_ids:
                        changed = True

                    if is_alternative:
                        alt_wait_bind_ids = alt_app_wait_bind_ids.get(next_bind_id)
                        if alt_wait_bind_ids is not None:
                            name_num_count: Dict[str, Dict[int, int]] = {}
                            for name, num_conds in name_to_num_conds.items():
                                if name == _condition_key:
                                    continue

                                num_count = {}

                                exist_suitable = True
                                next_alt_wait_bind_ids = alt_wait_bind_ids[name]
                                for num, cond in num_conds:
                                    num_next_alt_wait_bind_ids = next_alt_wait_bind_ids[num]
                                    if num_next_alt_wait_bind_ids is None:
                                        continue

                                    if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or \
                                            (not runned and cond == False):
                                        num_count[num] = 1

                                        if is_processor:
                                            alt_dep_key = (run_id, next_bind_id, next_iteration, name, num)
                                            deps = self.__alt_deps.get(alt_dep_key)
                                            if deps is None:
                                                deps = {}
                                                self.__alt_deps[alt_dep_key] = deps

                                            if bind_id not in deps:
                                                self.__prepare_next_collections(loop_structures.collections_binds_funcs, (next_bind_id, next_iteration), bind_id, iteration)
                                                deps[bind_id] = iteration

                                        if bind_id not in num_next_alt_wait_bind_ids:
                                            continue

                                        num_next_alt_wait_bind_ids.pop(bind_id)
                                        if len(num_next_alt_wait_bind_ids) == 0:
                                            if alt_wait_bind_ids.pop(name, None) is None:
                                                raise EntityException(f"several alternative arguments are suitable for name={name} in {next_bind_id}")
                                            if len(alt_wait_bind_ids) == 0:
                                                alt_app_wait_bind_ids.pop(next_bind_id)
                                                exist_alt_bind_ids = False
                                    else:
                                        num_count[num] = -1
                                        next_alt_wait_bind_ids[num] = None
                                        exist_suitable = False
                                        for next_num_conds in next_alt_wait_bind_ids:
                                            if next_num_conds is not None:
                                                exist_suitable = True
                                                break
                                        if not exist_suitable:
                                            alt_app_wait_bind_ids[next_bind_id] = None
                                            next_bind_id_copy = next_bind_id
                                            run_next_tasks.append(lambda: self.__run_next(run_id, next_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                                            struct_update.count_app(next_index, next_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], name_num_count={})
                                            name_num_count.clear()
                                            break

                                if not exist_suitable:
                                    break
                                if len(num_count) > 0:
                                    name_num_count[name] = num_count
                            if len(name_num_count) > 0:
                                struct_update.count_app(next_index, next_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], name_num_count=name_num_count)

                    need_run = changed and need_run_plain and not exist_alt_bind_ids and not exist_bind_ids_conds
                else:
                    first = True
                    for cluster_index in clusters_indices_next:
                        cluster_iteration = iterations_connection_wrapper[cluster_index]

                        changed = False

                        iter_to_app_wait_bind_ids = loop_structures.app_wait_bind_ids.get(cluster_index)
                        if iter_to_app_wait_bind_ids is None:
                            iter_to_app_wait_bind_ids = {}
                            loop_structures.app_wait_bind_ids[cluster_index] = iter_to_app_wait_bind_ids

                        app_wait_bind_ids: Dict[str, Dict[str, Optional[bool]]] = iter_to_app_wait_bind_ids.get(cluster_iteration)
                        if app_wait_bind_ids is None:
                            app_wait_bind_ids = copy.deepcopy(self.__cluster_wait_bind_ids[cluster_index])
                            iter_to_app_wait_bind_ids[cluster_iteration] = app_wait_bind_ids

                        wait_bind_ids = app_wait_bind_ids.get(next_bind_id)
                        need_run_plain = wait_bind_ids is None or len(wait_bind_ids) == 0

                        if runned and is_plain and wait_bind_ids is not None:
                            struct_update.count_app(cluster_index, cluster_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index])
                            wait_bind_id_res = wait_bind_ids[bind_id]
                            if wait_bind_id_res is None or wait_bind_id_res == cond_value or (cond_value is None and wait_bind_id_res):
                                wait_bind_ids.pop(bind_id)
                                changed = True
                                if first and is_processor:
                                    self.__prepare_next_collections(loop_structures.collections_binds_funcs, (next_bind_id, next_bind_id_pair[1]), bind_id, iteration)
                                if len(wait_bind_ids) == 0:
                                    app_wait_bind_ids.pop(next_bind_id)
                                    need_run_plain = True
                            else:
                                app_wait_bind_ids[next_bind_id] = None
                                if first:
                                    next_bind_id_copy = next_bind_id
                                    run_next_tasks.append(lambda: self.__run_next(run_id, cluster_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                        app_wait_bind_ids_conds: Dict[str, List[Dict[str, Optional[bool]]]] = None
                        if is_condition or next_bind_id in self.__cluster_wait_bind_ids_conds[cluster_index]:
                            iter_to_app_wait_bind_ids_conds = loop_structures.app_wait_bind_ids_conds.get(cluster_index)
                            if iter_to_app_wait_bind_ids_conds is None:
                                iter_to_app_wait_bind_ids_conds = {}
                                loop_structures.app_wait_bind_ids_conds[cluster_index] = iter_to_app_wait_bind_ids_conds

                            app_wait_bind_ids_conds = iter_to_app_wait_bind_ids_conds.get(cluster_iteration)
                            if app_wait_bind_ids_conds is None:
                                app_wait_bind_ids_conds = copy.deepcopy(self.__cluster_wait_bind_ids_conds[cluster_index])
                                iter_to_app_wait_bind_ids_conds[cluster_iteration] = app_wait_bind_ids_conds
                        exist_bind_ids_conds = app_wait_bind_ids_conds is not None and next_bind_id in app_wait_bind_ids_conds
                        if exist_bind_ids_conds:
                            changed = True

                        if is_condition:
                            wait_bind_ids_conds = app_wait_bind_ids_conds.get(next_bind_id)
                            if wait_bind_ids_conds is not None:
                                num_count: Dict[int, int] = {}
                                num_conds = name_to_num_conds[_condition_key]

                                for num, cond in num_conds:
                                    num_next_wait_bind_ids_conds = wait_bind_ids_conds[num]
                                    if num_next_wait_bind_ids_conds is None:
                                        continue

                                    if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or \
                                            (not runned and cond == False):
                                        num_count[num] = 1
                                        if bind_id not in num_next_wait_bind_ids_conds:
                                            continue

                                        num_next_wait_bind_ids_conds.pop(bind_id)
                                        if len(num_next_wait_bind_ids_conds) == 0:
                                            app_wait_bind_ids_conds.pop(next_bind_id)
                                            exist_bind_ids_conds = False
                                    else:
                                        num_count[num] = -1
                                        wait_bind_ids_conds[num] = None
                                        exist_suitable = False
                                        for next_num_conds in wait_bind_ids_conds:
                                            if next_num_conds is not None:
                                                exist_suitable = True
                                                break
                                        if not exist_suitable:
                                            app_wait_bind_ids_conds[next_bind_id] = None
                                            if first:
                                                next_bind_id_copy = next_bind_id
                                                run_next_tasks.append(lambda: self.__run_next(run_id, cluster_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                                                struct_update.count_app(cluster_index, cluster_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], num_count={})
                                                num_count.clear()
                                                break

                                if len(num_count) > 0:
                                    struct_update.count_app(cluster_index, cluster_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], num_count=num_count)

                        alt_app_wait_bind_ids: Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]] = None
                        if is_alternative or next_bind_id in self.__alt_cluster_wait_bind_ids[cluster_index]:
                            iter_to_alt_app_wait_bind_ids = loop_structures.alt_app_wait_bind_ids.get(cluster_index)
                            if iter_to_alt_app_wait_bind_ids is None:
                                iter_to_alt_app_wait_bind_ids = {}
                                loop_structures.alt_app_wait_bind_ids[cluster_index] = iter_to_alt_app_wait_bind_ids

                            alt_app_wait_bind_ids = iter_to_alt_app_wait_bind_ids.get(cluster_iteration)
                            if alt_app_wait_bind_ids is None:
                                alt_app_wait_bind_ids = copy.deepcopy(self.__alt_cluster_wait_bind_ids[cluster_index])
                                iter_to_alt_app_wait_bind_ids[cluster_iteration] = alt_app_wait_bind_ids
                        exist_alt_bind_ids = alt_app_wait_bind_ids is not None and next_bind_id in alt_app_wait_bind_ids
                        if exist_alt_bind_ids:
                            changed = True

                        if is_alternative:
                            alt_wait_bind_ids = alt_app_wait_bind_ids.get(next_bind_id)
                            if alt_wait_bind_ids is not None:
                                name_num_count: Dict[str, Dict[int, int]] = {}
                                for name, num_conds in name_to_num_conds.items():
                                    if name == _condition_key:
                                        continue

                                    num_count = {}

                                    exist_suitable = True
                                    next_alt_wait_bind_ids = alt_wait_bind_ids[name]
                                    for num, cond in num_conds:
                                        num_next_alt_wait_bind_ids = next_alt_wait_bind_ids[num]
                                        if num_next_alt_wait_bind_ids is None:
                                            continue

                                        if (runned and (cond is None or cond == cond_value or (cond_value is None and cond))) or \
                                                (not runned and cond == False):
                                            num_count[num] = 1

                                            if first and is_processor:
                                                alt_dep_key = (run_id, next_bind_id, cluster_iteration, name, num)
                                                deps = self.__alt_deps.get(alt_dep_key)
                                                if deps is None:
                                                    deps = {}
                                                    self.__alt_deps[alt_dep_key] = deps

                                                if bind_id not in deps:
                                                    self.__prepare_next_collections(loop_structures.collections_binds_funcs, (next_bind_id, cluster_iteration), bind_id, iteration)
                                                    deps[bind_id] = iteration

                                            if bind_id not in num_next_alt_wait_bind_ids:
                                                continue

                                            num_next_alt_wait_bind_ids.pop(bind_id)
                                            if len(num_next_alt_wait_bind_ids) == 0:
                                                if alt_wait_bind_ids.pop(name, None) is None:
                                                    raise EntityException(f"several alternative arguments are suitable for name={name} in {next_bind_id}")
                                                if len(alt_wait_bind_ids) == 0:
                                                    alt_app_wait_bind_ids.pop(next_bind_id)
                                                    exist_alt_bind_ids = False
                                        else:
                                            num_count[num] = -1
                                            next_alt_wait_bind_ids[num] = None
                                            exist_suitable = False
                                            for next_num_conds in next_alt_wait_bind_ids:
                                                if next_num_conds is not None:
                                                    exist_suitable = True
                                                    break
                                            if not exist_suitable:
                                                alt_app_wait_bind_ids[next_bind_id] = None
                                                if first:
                                                    next_bind_id_copy = next_bind_id
                                                    run_next_tasks.append(lambda: self.__run_next(run_id, cluster_iteration, items, next_bind_id_copy, None, True, False, struct_update=struct_update))

                                                    struct_update.count_app(cluster_index, cluster_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], name_num_count={})
                                                    name_num_count.clear()
                                                    break

                                    if not exist_suitable:
                                        break
                                    if len(num_count) > 0:
                                        name_num_count[name] = num_count
                                if len(name_num_count) > 0:
                                    struct_update.count_app(cluster_index, cluster_iteration, next_bind_id, iterations_connection_wrapper[next_bind_id_index], name_num_count=name_num_count)
                        if first:
                            need_run = changed and need_run_plain and not exist_alt_bind_ids and not exist_bind_ids_conds
                            first = False

                if need_run:
                    run_iteration = iterations_connection_wrapper[next_bind_id_index]
                    if next_bind_id not in loop_structures.zero_iteration_mapping:
                        loop_structures.zero_iteration_mapping[next_bind_id] = run_iteration
                        struct_update.zero_iteration_mapping[next_bind_id] = run_iteration
                    self.__set_collections_for_iteration(run_id, run_iteration + 1)
                    tasks.append(self.__run(run_id, run_iteration, items, next_bind_id))

        # self.__logs_buffer.write(f"loop_structures.iterations_connection after {loop_structures.iterations_connection} | {loop_structures.iterations_transition}\n")
        # self.__logs_buffer.write(f"loop_structures.iterations_connection diff {struct_update.iterations_connection} | {struct_update.iterations_transition}\n")

        for task in run_next_tasks:
            new_tasks, _ = task()
            tasks.extend(new_tasks)
        return tasks, struct_update

    async def init(self) -> bool:
        tasks = []
        for item in self.__items.values():
            tasks.append(item.japp.init_all_first())

        try:
            self.__cur_task = gather(*tasks)
            return all(await self.__cur_task)
        except:
            return False
        finally:
            self.__cur_task = None

    async def init_run(self, init: InitRun) -> Optional[bool]:
        run_id = init.runId
        assert run_id not in self.__run_items, f"run with id = {run_id} already exist"

        items = {}
        self.__run_items[run_id] = items

        if init.cfg is None:
            cfg, app_cfg_extension_all = self.__common_cfg, {}
        else:
            cfg, app_cfg_extension_all = do_cfg(init.cfg, init.infoUrl, all_extension_keys=True)

        pauses = self.__run_pauses.get(run_id)
        if pauses is None:
            pauses = {}
            self.__run_pauses[init.runId] = pauses

        tasks = []
        for bind_id, item in self.__items.items():
            new_j_app = self.__registry.create_app(init, bind_id, cfg, app_cfg_extension=app_cfg_extension_all.get(f"${bind_id}"), local_dfs=self.__collections_holder.local_dfs)
            new_j_app._set_pauses(pauses)
            new_item = JuliusPipelineItem(new_j_app, self.__hash)
            tasks.append(new_j_app.init_all())
            items[bind_id] = new_item
        if not all(await gather(*tasks)):
            return False

        cluster_next_iteration = {}
        cur_bind_ids = set()
        for bind_id in self.__items:
            cluster_next_iteration[self.__init.pipeline.bindIdToCluster[bind_id]] = 1
            cur_bind_ids.add(bind_id)
        for cur_clusters_indices in self.__init.clusters.values():
            for index in cur_clusters_indices:
                cluster_next_iteration[index] = 0
        loop_structures = self.__run_loop_structures.get(run_id)
        if loop_structures is None:
            self.__run_loop_structures[run_id] = RunLoopStructures(self.__bind_ids_list, self.__init.clusters, cluster_next_iteration=cluster_next_iteration, exist_bind_ids=cur_bind_ids)
        else:
            loop_structures.cluster_next_iteration = cluster_next_iteration
            loop_structures.not_runned_bind_ids = cur_bind_ids
        self.__run_wait_bind_ids[run_id] = copy.deepcopy(self.__wait_bind_ids)
        self.__run_wait_bind_ids_conds[run_id] = copy.deepcopy(self.__wait_bind_ids_conds)
        self.__run_alt_wait_bind_ids[run_id] = copy.deepcopy(self.__alt_wait_bind_ids)

        # FIXME remove
        # self.__logs_buffer.write(f"bindIdToCluster {self.__init.pipeline.bindIdToCluster}\n")
        # self.__logs_buffer.write(f"clusters {self.__init.clusters}\n")
        # self.__logs_buffer.write(f"nexts {self.__nexts}\n")
        # self.__logs_buffer.write(f"loop_nexts {self.__loop_nexts}\n")
        # self.__logs_buffer.write(f"wait_bind_ids {self.__wait_bind_ids}\n")
        # self.__logs_buffer.write(f"alt_nexts {self.__alt_nexts}\n")
        # self.__logs_buffer.write(f"alt_loop_nexts {self.__alt_loop_nexts}\n")
        # self.__logs_buffer.write(f"alt_wait_bind_ids {self.__alt_wait_bind_ids}\n")
        # self.__logs_buffer.write(f"nexts_conds {self.__nexts_conds}\n")
        # self.__logs_buffer.write(f"loop_nexts_conds {self.__loop_nexts_conds}\n")
        # self.__logs_buffer.write(f"wait_bind_ids_conds {self.__wait_bind_ids_conds}\n")
        # self.__logs_buffer.write(f"loopIterationIncrement {self.__init.loopIterationIncrement}\n")

        await self.__collections_holder.init()
        return True

    async def run(self, run_id: str, iteration: int, bind_id_run: str, data: Optional[Dict[str, Tuple[str, ...]]], conditions: Optional[Dict[str, bool]], structure_update: PipelineStructureUpdate, bind_id_iterations: Optional[Dict[str, int]]) -> bool:
        loop_structures = self.__run_loop_structures[run_id]
        # self.__logs_buffer.write(f"structure_update {structure_update}\n")
        # self.__logs_buffer.write(f"bind_id_iterations {bind_id_iterations}\n")
        loop_structures.update(structure_update)

        if bind_id_iterations is None:
            bind_id_iterations = {}
        if data is None:
            data = {}
        else:
            self.__set_collections_for_iteration(run_id, 1 if len(bind_id_iterations) == 0 else max(bind_id_iterations.values()) + 1)
            self.__collections_holder.set_collection_external(run_id, data, bind_id_iterations)     # TODO not need?
        if conditions is None:
            conditions = {}

        # self.__logs_buffer.write(f"data={data.keys()} conditions={conditions.keys()}\n")

        run_items = self.__run_items[run_id]

        runs = []
        if len(data) == 0 and len(conditions) == 0:
            assert iteration == 0, "internal error: wrong iteration without data"

            run_wait_bind_ids = self.__run_wait_bind_ids[run_id]
            run_wait_bind_ids_conds = self.__run_wait_bind_ids_conds[run_id]
            run_alt_wait_bind_ids = self.__run_alt_wait_bind_ids[run_id]
            for bind_id in self.__items:
                if bind_id not in run_wait_bind_ids and bind_id not in run_wait_bind_ids_conds and bind_id not in run_alt_wait_bind_ids:
                    loop_structures.zero_iteration_mapping[bind_id] = iteration
                    self.__set_collections_for_iteration(run_id, iteration + 1)
                    runs.append(self.__run(run_id, iteration, run_items, bind_id))
        else:
            for bind_id, coll_ids in data.items():
                conditions.pop(bind_id, None)   # just in case
                colls = list(map(get_collection_by_id, coll_ids))
                bind_id_iteration = bind_id_iterations[bind_id]

                if self.__scale.get(bind_id, 0) > 1 and self.__scale_index == 0:
                    await self.__save_collections(colls, run_items[bind_id], bind_id, save_force=True)

                tasks, _ = self.__run_next(run_id, bind_id_iteration, run_items, bind_id, None, with_update=False)
                runs.extend(tasks)
                self.__collections_holder.done(run_id, bind_id, bind_id_iteration, colls)   # not need also run .conds - it exists if needed

            for bind_id, cond_value in conditions.items():
                bind_id_iteration = bind_id_iterations[bind_id]

                tasks, _ = self.__run_next(run_id, bind_id_iteration, run_items, bind_id, cond_value, with_update=False)
                runs.extend(tasks)

            if len(conditions) > 0:
                self.__collections_holder.conds(run_id, iteration, conditions)

        if len(runs) == 0:
            if all([self.__scale.get(bind_id, 0) < 2 for bind_id in data.keys()]):
                self.__logs_buffer.write("warning: not enough data for continue pipeline\n")
            return True
        return all(await asyncio.gather(*runs))

    def runs(self) -> List[str]:
        return list(self.__run_items.keys())

    def logs(self, run_id: Optional[str] = None, clear: bool = False) -> Tuple[Dict[str, str], Dict[str, str]]:   # bind_id -> logs (common), bind_id -> logs (context.log)
        logs = {}
        user_logs = {}

        if run_id is None:
            items = self.__items
        else:
            items = self.__run_items.get(run_id, {})
        for bind_id, item in items.items():
            log = item.japp.logs_buffer.getvalue()
            if len(log) > 0:
                logs[bind_id] = log
            user_log = item.japp._context._logs(clear=clear)
            if len(user_log) > 0:
                user_logs[bind_id] = user_log
            if clear:
                item.japp.logs_buffer.truncate(0)
                item.japp.logs_buffer.seek(0)
        return logs, user_logs

    def get_input_collections(self, raises: bool = True) -> List[str]:
        res = []
        for _, item in self.__items.items():
            colls = item.japp.get_input_collections(raises=raises)
            if colls is not None:
                res.extend(colls)
        return res

    def set_for_kafka(self, run_id: str):
        for item in self.__run_items[run_id].values():
            item.japp.set_for_kafka()

    def exist_run(self, run_id: str) -> bool:
        return run_id in self.__run_items

    def any_run_japp(self, run_id: str) -> Optional['JuliusApp']:
        for item in self.__run_items.get(run_id, {}).values():
            return item.japp
        return None

    def stream(self, run_id: str, bind_id: str, *, remove: bool = False) -> Optional[callable]:
        streams = self.streams(run_id)
        if remove:
            return streams.pop(bind_id, None)
        else:
            return streams.get(bind_id)

    def streams(self, run_id: str) -> Dict[str, callable]:
        return self.__run_stream_res.get(run_id, {})

    def cancel(self, delete: bool = True):
        if self.__cur_task is not None:
            self.__cur_task.cancel()
        if delete:
            for run_id in self.__run_items.keys():
                self.delete_run(run_id)
        else:
            for run_items in self.__run_items.values():
                for item in run_items.values():
                    item.japp.cancel()

    def delete_run(self, run_id: str):
        self.__alt_deps = {k: v for k, v in self.__alt_deps.items() if k[0] != run_id}
        run_items = self.__run_items.pop(run_id, None)
        self.__run_collections.pop(run_id, None)
        self.__run_loop_structures.pop(run_id, None)
        self.__run_wait_bind_ids.pop(run_id, None)
        self.__run_wait_bind_ids_conds.pop(run_id, None)
        self.__run_alt_wait_bind_ids.pop(run_id, None)
        self.__run_stream_res.pop(run_id, None)
        self.__run_pauses.pop(run_id, None)
        self.__set_collections_next_iteration_by_run_id.pop(run_id, None)
        self.__collections_holder.delete_run(run_id)

        if run_items is not None:
            for item in run_items.values():
                item.japp.cancel()
