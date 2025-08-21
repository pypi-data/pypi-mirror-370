from typing import Optional, List, Tuple, Dict
from malevich_app.export.jls.df import JDF


class LocalDfs:     # FIXME types: not real JDF - pd.DataFrame/Dict/List/BaseModel
    def __init__(self):
        self._data: Dict[int, Tuple[JDF, Optional[str]]] = {}
        self._next_id = 0

    def filter(self, df_id: int, ids: List[str]):
        assert df_id < self._next_id, "wrong id"
        self._data[df_id] = (self._data[df_id][0][self._data[df_id][0]["__id__"].isin(ids)], self._data[df_id][1])

    def get(self, id: int) -> Tuple[Optional[JDF], Optional[str]]:
        return self._data[id] if id < self._next_id else None

    def update(self, id: int, df: JDF, scheme_name: Optional[str]):
        self._data[id] = (df, scheme_name)

    def post(self, df: JDF = None, scheme_name: Optional[str] = None) -> int:
        self._data[self._next_id] = (df, scheme_name)
        self._next_id += 1
        return self._next_id - 1

    def delete(self, id: int):
        self._data.pop(id)
