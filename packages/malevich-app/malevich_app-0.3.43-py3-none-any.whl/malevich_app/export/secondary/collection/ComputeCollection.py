from typing import Callable, Dict, Coroutine, Any
from malevich_app.export.secondary.collection.Collection import Collection


class ComputeCollection(Collection):
    def __init__(self, f: Callable[[Dict[str, str]], Coroutine[Any, Any, Collection]]):
        self.__f = f
        self.__collection: Collection = None

    async def compute(self, collections: Dict[str, str]):
        self.__collection = await self.__f(collections)

    def get(self):
        assert self.__collection is not None, "compute collection isn't ready"
        return self.__collection.get()

    def get_collection(self) -> Collection:
        assert self.__collection is not None, "compute collection isn't ready"
        return self.__collection

    def get_mode(self) -> str:
        return "not_check"
