from typing import List, Dict, Set, Optional, Callable, Tuple

from malevich_app.export.abstract.abstract import PipelineStructureUpdate
from malevich_app.export.secondary.structs import DictWrapper


class RunLoopStructures:
    def __init__(self, bind_ids_list: List[str], clusters: Dict[str, Set[int]], cluster_next_iteration: Dict[int, int] = None, exist_bind_ids: Set[str] = None):
        self.__bind_ids_list: List[str] = bind_ids_list
        self.__clusters: Dict[str, Set[int]] = clusters

        self.app_wait_bind_ids: Dict[int, Dict[int, Dict[str, Dict[str, Optional[bool]]]]] = {}                         # cluster -> iteration -> __wait_bind_ids or __loop_wait_bind_ids copy  # TODO fix comment?
        self.app_wait_bind_ids_conds: Dict[int, Dict[int, Dict[str, List[Dict[str, Optional[bool]]]]]] = {}             # cluster -> iteration -> __wait_bind_ids_conds or __loop_wait_bind_ids_conds copy
        self.alt_app_wait_bind_ids: Dict[int, Dict[int, Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]]]] = {}    # cluster -> iteration -> __alt_wait_bind_ids or __alt_loop_wait_bind_ids copy
        self.iterations_connection: Dict[Tuple[int, int], DictWrapper[Dict[int, int]]] = {}                             # (cl num, iter) -> cl num2 -> iter2
        self.iterations_transition: Dict[Tuple[int, int], DictWrapper[Dict[int, int]]] = {}                             # (cl num, iter) -> cl num2 -> iter2
        self.iterations_transition_prev: Dict[Tuple[int, int], Set[DictWrapper[Dict[int, int]]]] = {}                   # (cl num, iter) -> set cl num2 -> iter2
        self.cluster_next_iteration: Dict[int, int] = {} if cluster_next_iteration is None else cluster_next_iteration  # cluster id or bindId -> iteration

        self.not_runned_bind_ids: Set[str] = exist_bind_ids if exist_bind_ids is not None else set()
        self.collections_binds_funcs: Dict[Tuple[str, int], Dict[str, List[Callable[[int], None]]]] = {}
        self.dict_wrapper_index = 0     # FIXME ok?
        self.zero_iteration_mapping: Dict[str, int] = {}

    def update(self, structure_update: PipelineStructureUpdate):
        for cluster_from, cur_iterations_to_pairs in structure_update.iterationsConnection.items():
            for cur_iteration_from, pairs in cur_iterations_to_pairs.items():
                pairs[cluster_from] = cur_iteration_from

                dicts = set()
                for cluster, cur_iteration in pairs.items():
                    conn_pairs = self.iterations_connection.get((cluster, cur_iteration))
                    if conn_pairs is not None:
                        dicts.add(conn_pairs)

                if len(dicts) == 0:
                    pairs_wrapper = DictWrapper(self.dict_wrapper_index, pairs)
                    self.dict_wrapper_index += 1
                    for cluster, cur_iteration in pairs.items():
                        self.iterations_connection[(cluster, cur_iteration)] = pairs_wrapper
                else:
                    pairs_wrapper = None
                    if len(dicts) == 1:
                        for d in dicts:
                            pairs_wrapper = d
                    else:
                        for d in dicts:
                            if pairs_wrapper is None:
                                pairs_wrapper = d
                            else:
                                for cluster, cur_iteration in d.items():
                                    pairs_wrapper[cluster] = cur_iteration
                                    pairs.pop(cluster, None)
                                d.data = pairs_wrapper.data

                    for cluster, cur_iteration in pairs.items():
                        if cluster not in pairs_wrapper:
                            pairs_wrapper[cluster] = cur_iteration
                            self.iterations_connection[(cluster, cur_iteration)] = pairs_wrapper

        for cluster_from, cur_iterations_to_pairs in structure_update.iterationsTransition.items():
            for cur_iteration_from, iterations_transition in cur_iterations_to_pairs.items():
                iterations_transition_wrapper = DictWrapper(self.dict_wrapper_index, iterations_transition)
                self.dict_wrapper_index += 1

                iterations_connect_dict = self.iterations_connection.get((cluster_from, cur_iteration_from))
                if iterations_connect_dict is None:
                    iterations_connect_dict = {}
                else:
                    iterations_connect_dict = iterations_connect_dict.data

                bind_id = self.__bind_ids_list[-(cluster_from+1)]
                cur_clusters = self.__clusters[bind_id]
                if len(cur_clusters) != 0:
                    for conn_cluster, conn_iteration in iterations_connect_dict.items():
                        # if conn_cluster < 0:
                        #     continue

                        conn_iterations_transition_wrapper = self.iterations_transition.get((conn_cluster, conn_iteration))
                        if conn_iterations_transition_wrapper is None:
                            self.iterations_transition[(conn_cluster, conn_iteration)] = iterations_transition_wrapper
                        else:
                            for cluster, cluster_iteration in conn_iterations_transition_wrapper.items():
                                iterations_transition[cluster] = cluster_iteration
                            conn_iterations_transition_wrapper.data = iterations_transition
                else:
                    conn_iterations_transition_wrapper = self.iterations_transition.get((cluster_from, cur_iteration_from))
                    if conn_iterations_transition_wrapper is not None:
                        conn_iterations_transition = conn_iterations_transition_wrapper.data
                        for cluster, cluster_iteration in iterations_transition.items():
                            conn_iterations_transition[cluster] = cluster_iteration
                    else:
                        self.iterations_transition[(cluster_from, cur_iteration_from)] = iterations_transition_wrapper

        for index, iteration in structure_update.clusterNextIteration.items():
            self.cluster_next_iteration[index] = iteration

        for bind_id, iteration in structure_update.zeroIterationMapping.items():
            self.zero_iteration_mapping[bind_id] = iteration
