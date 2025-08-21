from typing import Dict, TypeVar, Generic, Union, Any

DictType = TypeVar("DictType")


class DictWrapper(Generic[DictType]):
    def __init__(self, hash: Any, data: DictType):
        self.__hash = hash
        self.data: Union[DictType, Dict] = data

    def clear(self):
        return self.data.clear()

    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def pop(self, k, d=None):
        return self.data.pop(k, d=d)

    def popitem(self, *args, **kwargs):
        return self.data.popitem(*args, **kwargs)

    def setdefault(self, *args, **kwargs):
        return self.data.setdefault(*args, **kwargs)

    def update(self, E=None, **F):
        return self.data.update(E=E, **F)

    def values(self):
        return self.data.values()

    def __class_getitem__(self, *args, **kwargs):
        return self.data.__class_getitem__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.data.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.data.__delitem__(*args, **kwargs)

    def __eq__(self, other):
        if isinstance(other, DictWrapper):
            return self.data.__eq__(other.data)
        return self.data.__eq__(other)

    def __getitem__(self, y):
        return self.data.__getitem__(y)

    def __ge__(self, *args, **kwargs):
        return self.data.__ge__(*args, **kwargs)

    def __gt__(self, *args, **kwargs):
        return self.data.__gt__(*args, **kwargs)

    def __ior__(self, *args, **kwargs):
        return self.data.__ior__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.data.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.data.__len__(*args, **kwargs)

    def __le__(self, *args, **kwargs):
        return self.data.__le__(*args, **kwargs)

    def __lt__(self, *args, **kwargs):
        return self.data.__lt__(*args, **kwargs)

    def __ne__(self, *args, **kwargs):
        return self.data.__ne__(*args, **kwargs)

    def __or__(self, *args, **kwargs):
        return self.data.__or__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.data.__repr__(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        return self.data.__reversed__(*args, **kwargs)

    def __ror__(self, *args, **kwargs):
        return self.data.__ror__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.data.__setitem__(*args, **kwargs)

    def __sizeof__(self):
        return self.data.__sizeof__()

    def __hash__(self):
        return self.__hash
