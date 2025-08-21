from malevich_app.export.secondary.collection.Collection import Collection


class DummyCollection(Collection):
    def get(self):
        return ""

    def get_mode(self) -> str:
        return "not_check"
