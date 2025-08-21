from typing import Optional, Tuple, Union, Dict
import pandas as pd
from pydantic import BaseModel

from malevich_app.export.abstract.abstract import FixScheme
from malevich_app.export.secondary.collection.Collection import Collection


async def get_df(julius_app, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[pd.DataFrame, Collection]:
    pass


async def get_doc_data(julius_app, id: str, fix_scheme: Optional[FixScheme]) -> Tuple[Union[Dict, BaseModel], Collection]:
    pass


async def get_df_object_record(julius_app, id: str) -> Tuple[pd.DataFrame, Collection]:
    pass


async def get_df_local(julius_app, id: int, scheme_name_to: Optional[str]) -> Tuple[pd.DataFrame, Collection]:
    pass


async def get_df_share(julius_app, id: str, scheme_name_to: Optional[str]) -> Tuple[pd.DataFrame, Collection]:
    pass


def save_df_local(julius_app, df: pd.DataFrame, scheme_name: Optional[str] = None) -> Collection:
    pass
