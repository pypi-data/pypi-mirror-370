from typing import List, Iterator
from malevich_app.export.secondary.collection.Collection import Collection


class CompositeCollection(Collection):
    def __init__(self, data: List[Collection]):
        self.__data = data
        self.__id = None

    def __iter__(self) -> Iterator[Collection]:
        return iter(self.__data)

    def get(self) -> List[Collection]:  # Mongo, Object, Local
        return self.__data

    def get_mode(self) -> str:
        return "not_check"
