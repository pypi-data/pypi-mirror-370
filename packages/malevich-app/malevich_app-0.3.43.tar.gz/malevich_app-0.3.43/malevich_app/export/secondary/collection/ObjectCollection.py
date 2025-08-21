import pandas as pd
from malevich_app.export.secondary.collection.Collection import Collection


class ObjectCollection(Collection):
    prefix = "$"

    def __init__(self, collection_id: str, with_prefix: bool = True, *, is_new: bool = False):     # path for collection object
        self.__is_new = is_new
        if with_prefix:
            assert collection_id.startswith(self.prefix), "wrong id for collection object - without prefix"
            self.__collection_id = collection_id[len(self.prefix):]
        else:
            self.__collection_id = collection_id

    def get(self, with_prefix: bool = False):
        if with_prefix:
            return f"{self.prefix}{self.__collection_id}"
        return self.__collection_id

    @property
    def df(self):
        return pd.DataFrame.from_dict({"path": [self.__collection_id]})

    @property
    def _is_new(self) -> bool:
        return self.__is_new

    def get_mode(self) -> str:
        return "not_check"
