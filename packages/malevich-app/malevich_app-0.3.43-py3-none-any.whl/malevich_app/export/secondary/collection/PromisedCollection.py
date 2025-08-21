from typing import List, Optional
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.CompositeCollection import CompositeCollection


class PromisedCollection(Collection):
    def __init__(self, indices: Optional[List[int]]):
        self.__indices = indices
        self.__res = None

    def set_result(self, res: List[Collection]):
        if self.__indices is None:
            self.__res = CompositeCollection(res)
        else:
            self.__res = CompositeCollection([res[i] for i in self.__indices])  # TODO check somewhere before that it have enough arguments

    def get(self):
        assert self.__res is not None, f"internal error: promised collection not set, {self}"
        return self.__res.get()

    def get_mode(self) -> str:
        return "not_check"
