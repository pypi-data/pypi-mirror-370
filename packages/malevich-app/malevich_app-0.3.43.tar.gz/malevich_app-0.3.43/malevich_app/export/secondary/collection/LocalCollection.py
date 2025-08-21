from malevich_app.export.secondary.collection.Collection import Collection


class LocalCollection(Collection):
    def __init__(self, collection_id: int, is_doc: bool = False):
        self.__collection_id = collection_id
        self.__is_doc = is_doc

    def get(self):
        return self.__collection_id

    def is_doc(self):
        return self.__is_doc

    def get_mode(self) -> str:
        return "not_check"
