from logging import Logger
from typing import List, Optional, Tuple, Any, Dict

spark = None    # not None only in pyspark mode
docker_mode = "example mode"


async def input_fun(julius_app, collections: List[Tuple[str, ...]], logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    pass


async def processor_fun(julius_app, logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    pass


async def output_fun(julius_app, logger: Logger) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    pass
