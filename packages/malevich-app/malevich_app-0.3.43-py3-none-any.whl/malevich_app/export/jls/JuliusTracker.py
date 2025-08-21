import traceback
from typing import Optional, List
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import PipelineAppFinished, PipelineStructureUpdate
from malevich_app.export.request.dag_requests import send_post_dag
from malevich_app.export.secondary.collection.Collection import Collection
from malevich_app.export.secondary.collection.JsonCollection import JsonCollection
from malevich_app.export.secondary.collection.ObjectCollection import ObjectCollection
from malevich_app.export.secondary.endpoints import PIPELINE_FINISH

class JuliusTracker:
    def __init__(self, dag_host_port: str, is_local: bool, index: int):
        self.__dag_host_port = dag_host_port
        self.__is_local = is_local
        self.__index = index

    async def finished(self, operation_id: str, run_id: str, bind_id: str, iteration: int, ok: bool, structure_update: PipelineStructureUpdate, *, colls: Optional[List[Collection]] = None, branch: Optional[bool] = None, hash: Optional[str] = None):
        if colls is not None:
            colls = list(map(lambda x: str(x.get(with_prefix=True)) if isinstance(x, ObjectCollection) or isinstance(x, JsonCollection) else str(x.get()), colls))
        data = PipelineAppFinished(operationId=operation_id, runId=run_id, bindId=bind_id, index=self.__index, iteration=iteration, collections=colls, branch=branch, ok=ok, structureUpdate=structure_update, hash=hash or "")

        if not self.__is_local:
            try:
                await send_post_dag(data.model_dump_json(), PIPELINE_FINISH(self.__dag_host_port), operation_id=operation_id)
            except:
                if C.WS is None:
                    print(traceback.format_exc())   # FIXME

            # send_background_task(send_post_dag, data.model_dump_json(), PIPELINE_FINISH(self.__dag_host_port))   # FIXME
            # await asyncio.sleep(C.SLEEP_BACKGROUND_TASK_S)
