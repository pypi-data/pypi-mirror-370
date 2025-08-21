from malevich_app.export.secondary.collection.Collection import Collection


class JsonCollection(Collection):   # TODO add extra local collection
    prefix = "#"

    def __init__(self, collection_id: str):
        assert collection_id.startswith(self.prefix), "wrong id for collection object - without prefix"
        self.__collection_id = collection_id[len(self.prefix):]

    def get(self, with_prefix: bool = False):
        if with_prefix:
            return f"{self.prefix}{self.__collection_id}"
        return self.__collection_id

    def get_mode(self) -> str:
        return "not_check"
