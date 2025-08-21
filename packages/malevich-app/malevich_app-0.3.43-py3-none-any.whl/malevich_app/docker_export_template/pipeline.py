from logging import Logger
from typing import List, Tuple, Optional

from malevich_app.export.jls.df import JDF
from malevich_app.export.secondary.collection.Collection import Collection


async def run_processor(julius_app, dfs: List[JDF], logger: Logger) -> Tuple[bool, Optional[List[Tuple[Collection]]]]:
    pass


async def run_condition(julius_app, dfs: List[JDF], logger: Logger) -> Tuple[bool, bool]:
    pass


async def run_output(julius_app, collections: List[Tuple[Collection]], logger: Logger) -> Tuple[bool, List[Collection]]:
    pass
