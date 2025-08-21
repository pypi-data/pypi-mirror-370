from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.helpers import read_df, save_collection


class FileCollection(Collection):   # TODO(add scheme)
    def __init__(self, filename: str, operation_id: str, mode: str = "check"):
        self.filename = filename
        self.__mode = mode
        self.__collection_id = self.__save(operation_id)

    def __save(self, operation_id: str):
        df = read_df(self.filename)
        return save_collection(df, operation_id).get()

    def get(self):
        return self.__collection_id

    def get_mode(self) -> str:
        return self.__mode
