from typing import List, Dict, Tuple, Callable, Optional

from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.collection.Collection import Collection


class VariantCollection(Collection):
    def __init__(self, run_id: str, iteration: int, collections: List[Tuple[Tuple[Callable[[str, int], Collection], ...], Optional[Dict[str, bool]]]], is_sink: bool):
        self.__run_id = run_id
        self.__iteration = iteration
        self.__is_sink = is_sink
        self.__conds: Dict[str, List[Tuple[bool, int]]] = {}
        self.__cond_wait: Dict[int, int] = {}
        self.__collections: List[Tuple[Callable[[str, int], Collection], ...]] = []
        self.__num: Optional[int] = None
        self.__res: Tuple[Collection, ...] = None

        for i, (colls, conds) in enumerate(collections):
            self.__collections.append(colls)

            if conds is None:
                if len(collections) != 1:
                    raise EntityException("conditions not set for not unique alternative argument")
                self.__num = i
                return

            self.__cond_wait[i] = len(conds)
            for cond, value in conds.items():
                conds_list = self.__conds.get(cond)
                if conds_list is None:
                    conds_list = []
                    self.__conds[cond] = conds_list
                conds_list.append((value, i))

    def __collection(self, num: int) -> Tuple[Collection, ...]:
        res = []
        for coll in self.__collections[num]:
            res.append(coll(self.__run_id, self.__iteration))
        return tuple(res)

    def set_conds(self, conds: Dict[str, bool]):
        nums = set()
        for cond, value in conds.items():
            values = self.__conds.pop(cond, None)
            if values is not None:
                for expected_value, num in values:
                    if value == expected_value:
                        self.__cond_wait[num] -= 1
                        nums.add(num)

        for num in nums:
            if self.__cond_wait[num] == 0:
                if self.__num is not None:
                    raise EntityException("several alternative arguments match the conditions")
                self.__num = num

    def is_sink(self) -> bool:
        return self.__is_sink

    def get(self) -> Tuple[Collection, ...]:
        if self.__res is not None:
            return self.__res

        if self.__num is None:
            raise EntityException("none of alternative arguments match the conditions")
        self.__res = self.__collection(self.__num)
        return self.__res

    def get_mode(self) -> str:
        return "not_check"
