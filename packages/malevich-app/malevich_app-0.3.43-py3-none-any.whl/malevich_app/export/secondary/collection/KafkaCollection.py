from malevich_app.export.secondary.collection.Collection import Collection


class KafkaCollection(Collection):
    def __init__(self, collection_id: str):
        self.__collection_id = collection_id

    def get(self):
        return self.__collection_id

    def get_mode(self) -> str:
        return "not_check"
