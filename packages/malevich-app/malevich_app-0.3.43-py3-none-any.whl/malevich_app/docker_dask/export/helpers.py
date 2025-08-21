import json
import os
from typing import Optional, Dict, Any, Tuple
from uuid import uuid4
import malevich_app.export.secondary.const as C
import dask.dataframe as dd
from malevich_app.export.secondary.LocalDfs import LocalDfs
from malevich_app.export.secondary.helpers import save_df, read_df


class LocalDfsSpark(LocalDfs):  # only for spark mode
    pass


def save_collection_dask(df: dd.DataFrame, operation_id: str, scheme: Optional[Dict[str, Any]]) -> str:
    coll_id = str(uuid4())
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    os.makedirs(path, exist_ok=True)    # mb override
    save_df(df, f"{path}/data", single_file=True)
    if scheme is not None:
        with open(f"{path}/scheme.json", 'w') as f:
            json.dump(scheme, f)
    return coll_id


def get_collection_dask(coll_id: str, operation_id: str) -> Tuple[dd.DataFrame, Optional[Dict[str, Any]], Optional[str]]:
    path = f"{C.COLLECTIONS_PATH(operation_id)}/{coll_id}"
    assert os.path.isfile(f"{path}/data") or (C.SAVE_DF_FORMAT != "csv" and os.path.isfile(f"{path}/data.csv")), "internal error: local collection not exist"
    if os.path.isfile(f"{path}/scheme.json"):
        with open(f"{path}/scheme.json", 'r') as f:
            scheme = json.load(f)
    else:
        scheme = None
    if os.path.isfile(f"{path}/metadata.json"):
        with open(f"{path}/metadata.json", 'r') as f:
            metadata = json.load(f)
    else:
        metadata = None
    return read_df(f"{path}/data", pkg=dd), scheme, metadata
