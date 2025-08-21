from typing import Dict, Optional, Tuple

from malevich_app.export.abstract.abstract import PipelineStructureUpdate, IntPair
from malevich_app.export.secondary.structs import DictWrapper


class StructureUpdate:
    def __init__(self):
        self.iterations_connection: Dict[Tuple[int, int], DictWrapper[Dict[int, int]]] = {}
        self.iterations_transition: Dict[Tuple[int, int], DictWrapper[Dict[int, int]]] = {}
        self.__app_wait_counts: Dict[int, Dict[int, Dict[str, IntPair]]] = {}
        self.__app_wait_counts_conds: Dict[int, Dict[int, Dict[str, Dict[int, Dict[int, int]]]]] = {}
        self.__alt_app_wait_counts: Dict[int, Dict[int, Dict[str, Dict[int, Dict[str, Dict[int, int]]]]]] = {}

        self.cluster_next_iteration: Dict[int, int] = {}
        self.zero_iteration_mapping: Dict[str, int] = {}

    def count_app(self, index: int, iteration: int, bind_id: str, bind_id_iteration: int, *, num_count: Optional[Dict[int, int]] = None, name_num_count: Optional[Dict[str, Dict[int, int]]] = None):
        is_condition = num_count is not None
        is_alternative = name_num_count is not None

        assert not is_alternative or not is_condition, "internal error in count_app"

        if is_alternative:
            index_app_wait_counts = self.__alt_app_wait_counts.get(index)
            if index_app_wait_counts is None:
                index_app_wait_counts = {}
                self.__alt_app_wait_counts[index] = index_app_wait_counts
        elif is_condition:
            index_app_wait_counts = self.__app_wait_counts_conds.get(index)
            if index_app_wait_counts is None:
                index_app_wait_counts = {}
                self.__app_wait_counts_conds[index] = index_app_wait_counts
        else:
            index_app_wait_counts = self.__app_wait_counts.get(index)
            if index_app_wait_counts is None:
                index_app_wait_counts = {}
                self.__app_wait_counts[index] = index_app_wait_counts

        app_wait_counts = index_app_wait_counts.get(iteration)
        if app_wait_counts is None:
            app_wait_counts = {}
            index_app_wait_counts[iteration] = app_wait_counts

        if is_alternative:
            bind_id_app_wait_counts = app_wait_counts.get(bind_id)
            if bind_id_app_wait_counts is None:
                bind_id_app_wait_counts = {}
                app_wait_counts[bind_id] = bind_id_app_wait_counts

            if len(name_num_count) == 0:
                bind_id_app_wait_counts[bind_id_iteration] = name_num_count
            else:
                cur_name_num_count = bind_id_app_wait_counts.get(bind_id_iteration)
                if cur_name_num_count is None:
                    bind_id_app_wait_counts[bind_id_iteration] = name_num_count
                else:
                    for name, num_count in name_num_count.items():
                        cur_num_count = cur_name_num_count.get(name)
                        if cur_num_count is None:
                            cur_name_num_count[name] = num_count
                        else:
                            for num, count in num_count.items():
                                if count < 0:   # not pass
                                    cur_num_count[num] = count
                                else:
                                    cur_num_count[num] = cur_num_count.get(num, 0) + count
        elif is_condition:
            bind_id_app_wait_counts = app_wait_counts.get(bind_id)
            if bind_id_app_wait_counts is None:
                bind_id_app_wait_counts = {}
                app_wait_counts[bind_id] = bind_id_app_wait_counts

            if len(num_count) == 0:
                bind_id_app_wait_counts[bind_id_iteration] = num_count
            else:
                cur_num_count = bind_id_app_wait_counts.get(bind_id_iteration)
                if cur_num_count is None:
                    bind_id_app_wait_counts[bind_id_iteration] = num_count
                else:
                    for num, count in num_count.items():
                        if count < 0:  # not pass
                            cur_num_count[num] = count
                        else:
                            cur_num_count[num] = cur_num_count.get(num, 0) + count
        else:
            pair = app_wait_counts.get(bind_id)
            if pair is None:
                pair = IntPair(first=bind_id_iteration, second=1)
                app_wait_counts[bind_id] = pair
            else:
                assert pair.first == bind_id_iteration, "iteration conflict"
                pair.second += 1

    def to_scheme(self) -> PipelineStructureUpdate:
        iterations_connection = {}
        for pair_from, pairs_to in self.iterations_connection.items():
            if len(pairs_to) > 0:
                iteration_to_pair = iterations_connection.get(pair_from[0])
                if iteration_to_pair is None:
                    iterations_connection[pair_from[0]] = {pair_from[1]: pairs_to}
                else:
                    iteration_to_pair[pair_from[1]] = pairs_to

        iterations_transition = {}
        for pair_from, pairs_to in self.iterations_transition.items():
            if len(pairs_to) > 0:
                iteration_to_pair = iterations_transition.get(pair_from[0])
                if iteration_to_pair is None:
                    iterations_transition[pair_from[0]] = {pair_from[1]: pairs_to}
                else:
                    iteration_to_pair[pair_from[1]] = pairs_to

        return PipelineStructureUpdate(iterationsConnection=iterations_connection, iterationsTransition=iterations_transition,
                                       clusterNextIteration=self.cluster_next_iteration, zeroIterationMapping=self.zero_iteration_mapping,
                                       appWaitCounts=self.__app_wait_counts, appWaitCountsConditions=self.__app_wait_counts_conds,
                                       alternativeAppWaitCounts=self.__alt_app_wait_counts)
