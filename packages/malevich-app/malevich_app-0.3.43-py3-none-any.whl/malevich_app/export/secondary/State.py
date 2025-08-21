from asyncio import Future
from io import StringIO
from typing import Optional, List, Dict, Any
from malevich_app.export.abstract.abstract import App


class State:
    def __init__(self, operation_id: str, schemes_names: List[str], scale: Optional[int] = None, *, app: Optional[App] = None, is_init_app: Optional[bool] = None, logs_buffer: Optional[StringIO] = None):
        self.operation_id = operation_id
        self.schemes_names = set(schemes_names)
        self.scale = scale

        # logs for operation_id
        self.logs_buffer = logs_buffer if logs_buffer is not None else StringIO()

        # app
        self.app = app
        self.is_init_app = is_init_app
        self.j_apps: Dict[str, Any] = {}    # run_id -> app
        self.base_j_app: Any = None

        # pipeline
        self.pipeline: 'JuliusPipeline' = None

        # other
        self.pauses: Dict[str, Dict[str, Future]] = {}  # run_id -> id -> future

states: Dict[str, State] = dict()
