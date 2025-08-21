import copy
from typing import Dict, Set, Any, Optional, List, Tuple

_inf = int(1e9-1)


def full_next_bind_ids(nexts: Dict[str, Set[str]], nexts_conds: Dict[str, Dict[str, Any]], alt_nexts: Dict[str, Dict[str, Any]]) -> Dict[str, Set[str]]:
    res = copy.deepcopy(nexts)
    for bind_id, cur_nexts in nexts_conds.items():
        full_nexts = res.get(bind_id)
        if full_nexts is None:
            full_nexts = set()
            res[bind_id] = full_nexts
        for next_bind_id in cur_nexts:
            full_nexts.add(next_bind_id)
    for bind_id, cur_nexts in alt_nexts.items():
        full_nexts = res.get(bind_id)
        if full_nexts is None:
            full_nexts = set()
            res[bind_id] = full_nexts
        for next_bind_id in cur_nexts:
            full_nexts.add(next_bind_id)
    return res


def full_wait_bind_ids(wait_bind_ids: Dict[str, Dict[str, Optional[bool]]], wait_bind_ids_conds:  Dict[str, List[Dict[str, bool]]], alt_wait_bind_ids: Dict[str, Dict[str, List[Dict[str, Optional[bool]]]]]) -> Dict[str, Set[str]]:
    res = {}
    for bind_id, deps in wait_bind_ids.items():
        cur_deps = res.get(bind_id)
        if cur_deps is None:
            cur_deps = set()
            res[bind_id] = cur_deps
        for dep_bind_id in deps:
            cur_deps.add(dep_bind_id)
    for bind_id, deps_list in wait_bind_ids_conds.items():
        cur_deps = res.get(bind_id)
        if cur_deps is None:
            cur_deps = set()
            res[bind_id] = cur_deps
        for deps in deps_list:
            for dep_bind_id in deps:
                cur_deps.add(dep_bind_id)
    for bind_id, name_to_deps_struct in alt_wait_bind_ids.items():
        cur_deps = res.get(bind_id)
        if cur_deps is None:
            cur_deps = set()
            res[bind_id] = cur_deps
        for deps_list in name_to_deps_struct.values():
            for deps in deps_list:
                for dep_bind_id in deps:
                    cur_deps.add(dep_bind_id)
    return res


def find_clusters(bind_ids: Dict[str, int], nexts: Dict[str, Set[str]]) -> Dict[str, Set[int]]:     # floyd + clustering
    if len(nexts) == 0:
        return {}

    bind_ids_list = [bind_id for bind_id in bind_ids]
    bind_ids_indices = {bind_id: i for i, bind_id in enumerate(bind_ids_list)}

    sz = len(bind_ids)
    next: List[List[Optional[int]]] = [[None] * sz for _ in range(sz)]
    dist: List[List[int]] = [[_inf] * sz for _ in range(sz)]

    for bind_id_from, nexts_bind_ids_to in nexts.items():
        from_index = bind_ids_indices[bind_id_from]
        for bind_id_to in nexts_bind_ids_to:
            to_index = bind_ids_indices[bind_id_to]
            dist[from_index][to_index] = 1
            next[from_index][to_index] = to_index

    for i in range(sz):
        dist[i][i] = 0
        next[i][i] = i

    for k in range(sz):
        for i in range(sz):
            for j in range(sz):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next[i][j] = next[i][k]

    #

    edge_to_cluster: Dict[Tuple[int, int], Set[int]] = {}
    index_iter = 0

    for bind_id_from, nexts_bind_ids_to in nexts.items():
        from_index = bind_ids_indices[bind_id_from]
        for bind_id_to in nexts_bind_ids_to:
            to_index = bind_ids_indices[bind_id_to]

            if dist[to_index][from_index] < _inf:
                indices_set = set()

                new_edges: List[Tuple[int, int]] = []
                edges: List[Tuple[int, int]] = []
                edge = (from_index, to_index)
                indices = edge_to_cluster.get(edge)
                if indices is None:
                    new_edges.append(edge)
                else:
                    for index in indices:
                        indices_set.add(index)
                    edges.append(edge)

                while from_index != to_index:
                    to_index_next = next[to_index][from_index]
                    edge = (to_index, to_index_next)
                    indices = edge_to_cluster.get(edge)
                    if indices is None:
                        new_edges.append(edge)
                    else:
                        for index in indices:
                            indices_set.add(index)
                        edges.append(edge)

                    to_index = to_index_next

                indices = list(indices_set)
                if len(indices) == 0:
                    for edge in edges:
                        edge_to_cluster[edge].add(index_iter)
                    for edge in new_edges:
                        edge_to_cluster[edge] = {index_iter}
                    index_iter += 1
                elif len(indices) == 1:
                    index = indices[0]
                    for edge in new_edges:
                        edge_to_cluster[edge] = {index}
                else:
                    index = indices[0]
                    indices = indices[1:]
                    for cluster_indices in edge_to_cluster.values():
                        exist = False
                        for i in indices:
                            if i in cluster_indices:
                                exist = True
                                break

                        if exist:
                            cluster_indices.add(index)
                            for i in indices:
                                cluster_indices.remove(i)

                    for edge in new_edges:
                        edge_to_cluster[edge] = {index}

    #

    clusters: Dict[str, Set[int]] = {}
    for edge, cluster_indices in edge_to_cluster.items():
        bind_id = bind_ids_list[edge[0]]    # not need [1] because of loops
        cur_clusters = clusters.get(bind_id)
        if cur_clusters is not None:
            for index in cluster_indices:
                cur_clusters.add(index)
        else:
            clusters[bind_id] = cluster_indices
    return clusters


def fix_clusters(clusters: Dict[str, Set[int]], bind_ids: Dict[str, int]) -> Dict[str, Set[int]]:
    if len(clusters) > 0:
        index = 0
        remapping: Dict[int, int] = {}
        for bind_id in bind_ids:
            indices = clusters.get(bind_id)
            if indices is not None:
                new_indices = set()
                for i in indices:
                    new_i = remapping.get(i)
                    if new_i is None:
                        new_i = index
                        remapping[i] = new_i
                        index += 1
                    new_indices.add(new_i)
                clusters[bind_id] = new_indices
    return clusters


def start_loop_bind_ids(bind_ids: Dict[str, int], nexts: Dict[str, Set[str]], wait_bind_ids: Dict[str, Set[str]], loop_nexts: Dict[str, Set[str]], clusters: Dict[str, set[int]]) -> Dict[str, Set[str]]:
    index = 0
    topsort_index: Dict[str, int] = {}

    def recursive_topsort(bind_id: str):
        nonlocal index

        topsort_index[bind_id] = index
        index += 1
        for next_bind_id in nexts.get(bind_id, []):
            wait_bind_ids[next_bind_id].remove(bind_id)
            if len(wait_bind_ids[next_bind_id]) == 0:
                recursive_topsort(next_bind_id)

    for bind_id in bind_ids:
        if bind_id not in wait_bind_ids:
            recursive_topsort(bind_id)

    #

    index = 0

    def recursive_loop_fun(bind_id: str, topsort_index: Dict[str, int], loop_topsort_index: Dict[str, int], nexts: Dict[str, Set[str]], wait_bind_ids: Dict[str, Set[str]], used: Set[str]) -> int:
        nonlocal index

        used.add(bind_id)
        count = 0

        loop_topsort_index[bind_id] = index
        index += 1

        for next_bind_id in nexts.get(bind_id):
            if next_bind_id in used:
                continue
            if topsort_index[bind_id] > topsort_index[next_bind_id]:
                continue

            wait_bind_ids[next_bind_id].remove(bind_id)
            count += 1
            if len(wait_bind_ids[next_bind_id]) == 0:
                count += recursive_loop_fun(next_bind_id, topsort_index, loop_topsort_index, nexts, wait_bind_ids, used)

        return count

    cluster_parts: Dict[int, List[str]] = {}
    for bind_id, indices in clusters.items():
        for index in indices:
            cluster_part = cluster_parts.get(index)
            if cluster_part is not None:
                cluster_part.append(bind_id)
            else:
                cluster_parts[index] = [bind_id]

    res: Dict[str, Set[str]] = {}

    for cluster_part in cluster_parts.values():
        cluster_part.sort(key=lambda bind_id: topsort_index[bind_id])
        cluster_part_set = set(cluster_part)

        count = 0
        cur_wait_bind_ids: Dict[str, Set[str]] = {}
        cur_nexts: Dict[str, Set[str]] = {}
        for bind_id in cluster_part:
            cur_bind_ids: Set[str] = set()
            for next_bind_id in loop_nexts.get(bind_id, []):
                if next_bind_id in cluster_part_set:
                    cur_bind_ids.add(next_bind_id)

                    next_cur_wait_bind_ids = cur_wait_bind_ids.get(next_bind_id)
                    if next_cur_wait_bind_ids is None:
                        next_cur_wait_bind_ids = set()
                        cur_wait_bind_ids[next_bind_id] = next_cur_wait_bind_ids
                    next_cur_wait_bind_ids.add(bind_id)

            cur_nexts[bind_id] = cur_bind_ids
            count += len(cur_bind_ids)

        loop_topsort_index: Dict[str, int] = {}
        used: Set[str] = set()
        for bind_id in cluster_part:
            if bind_id in used:
                continue

            for next_bind_id in cur_nexts.get(bind_id, []):
                if topsort_index[bind_id] < topsort_index[next_bind_id]:
                    continue

                cur_wait_bind_ids[next_bind_id].remove(bind_id)
                count -= 1
                if len(cur_wait_bind_ids[next_bind_id]) == 0:
                    count -= recursive_loop_fun(next_bind_id, topsort_index, loop_topsort_index, cur_nexts, cur_wait_bind_ids, used)

            if count <= 0:
                break

        assert count == 0, f"internal error: loop structure crate - negative count = {count}"
        assert len(used) == len(cluster_part), f"internal error: wrong used size - expected {len(cluster_part)}, found {len(used)}"
        assert len(loop_topsort_index) == len(cluster_part), f"internal error: wrong loop_topsort_index size - expected {len(cluster_part)}, found {len(loop_topsort_index)}"

        for bind_id_from, bind_ids_to in cur_nexts.items():
            for bind_id_to in bind_ids_to:
                if loop_topsort_index[bind_id_from] >= loop_topsort_index[bind_id_to]:
                    increment_from = res.get(bind_id_from)
                    if increment_from is None:
                        increment_from = set()
                        res[bind_id_from] = increment_from
                    increment_from.add(bind_id_to)

    return res
