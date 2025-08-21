from typing import Optional
from malevich_app.export.secondary.collection.Collection import Collection


class MongoCollection(Collection):
    def __init__(self, collection_id: str, mode: str = "not_check", *, base: Optional[Collection] = None):
        self.__collection_id = collection_id
        self.__mode = mode
        self.__base_collection = base

    def get(self):
        return self.__collection_id

    def base(self) -> Collection:
        return self.__base_collection or self

    def get_mode(self) -> str:
        return self.__mode
