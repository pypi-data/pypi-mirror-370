from typing import List
import pyspark.sql.functions as F
from malevich_app.export.secondary.LocalDfs import LocalDfs


class LocalDfsSpark(LocalDfs):
    def __init__(self):
        super().__init__()

    def filter(self, df_id: int, ids: List[str]):
        assert df_id < self._next_id, "wrong id"
        self._data[df_id] = (self._data[df_id][0].filter(F.col("__id__").isin(ids)), self._data[df_id][1])
