
class DummyAppWrapper:
    def get(self, *args, **kwargs):
        return lambda x: x

    def post(self, *args, **kwargs):
        return lambda x: x

    def delete(self, *args, **kwargs):
        return lambda x: x
