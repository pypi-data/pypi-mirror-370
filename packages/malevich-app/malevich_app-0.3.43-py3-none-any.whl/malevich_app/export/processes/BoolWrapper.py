class BoolWrapper:
    def __init__(self, val: bool = False):
        self.__val = val

    def set(self, val: bool):
        self.__val = val

    def __bool__(self):
        return self.__val
