import base64
import traceback
from typing import Dict, Optional, List, Callable, Any, Tuple, Type
from pydantic import BaseModel
from fastapi import Response, Request

from malevich_app.export.abstract.abstract import LogsOperation, GetAppInfo, InputCollections, FunMetadata, \
    InitPipeline, InitRun, RunPipeline, Init, Run, Collection, Objects, WSObjectsReq, RunStream, WSContinueReq, Cancel

_operations_mapping: Dict[str, any] = None


def __wrapper(fun: Callable, model: Optional[Type[BaseModel]] = None, with_response: bool = True, return_response: bool = False, keys_order: Optional[List[str]] = None, key_body: Optional[str] = None) -> Callable:   # key_body check only if keys_order exists
    async def internal_call(data: Optional[bytes]) -> Tuple[Optional[Any], Response]:
        data = None if model is None else model.model_validate_json(data)
        response = Response() if with_response else None
        request = None

        args = []
        if data is not None:
            if keys_order is not None:
                data = data.model_dump()
                for key in keys_order:
                    args.append(data.get(key))

                if key_body is not None:
                    body_str = data.get(key_body)
                    request = Request({"type": "http", "method": "POST"})
                    request._body = base64.b64decode(body_str)
            else:
                args.append(data)
        if request is not None:
            args.append(request)
        if with_response:
            args.append(response)

        try:
            res = await fun(*args)
        except BaseException as ex:
            print(traceback.format_exc())
            raise ex
        if return_response:
            return None, res
        else:
            return res, response
    return internal_call


def ws_init() -> Dict[str, any]:
    global _operations_mapping
    if _operations_mapping is None:
        import malevich_app.export.api.api as api
        _operations_mapping = {
            "ping": __wrapper(api.ping, with_response=False),
            "logs": __wrapper(api.logs, LogsOperation),
            "app_info": __wrapper(api.app_functions_info, GetAppInfo),
            "input": __wrapper(api.input_put, InputCollections),
            "processor": __wrapper(api.processor_put, FunMetadata),
            "output": __wrapper(api.output_put, FunMetadata),
            "init/pipeline": __wrapper(api.init_pipeline, InitPipeline),
            "init_run/pipeline": __wrapper(api.init_run_pipeline, InitRun, with_response=False, return_response=True),
            "run/pipeline": __wrapper(api.run_pipeline, RunPipeline),
            "init": __wrapper(api.init_put, Init),
            "init_run": __wrapper(api.init_run, InitRun, with_response=False, return_response=True),
            "run": __wrapper(api.run, Run),
            "stream": __wrapper(api.stream, RunStream),
            "finish": __wrapper(api.finish, FunMetadata, with_response=False, return_response=True),
            "collection": __wrapper(api.put_collection, Collection, with_response=False, return_response=True),
            "objects": __wrapper(api.put_objects, WSObjectsReq, with_response=False, return_response=True, keys_order=["operationId", "runId", "asset"], key_body="payload"),
            "objects/reverse": __wrapper(api.get_objects, Objects, with_response=False, return_response=True),
            "continue": __wrapper(api.continue_, WSContinueReq, with_response=False, return_response=True, keys_order=["operationId", "runId", "id"], key_body="payload"),
            "cancel": __wrapper(api.cancel, Cancel, with_response=False, return_response=True),
        }
    return _operations_mapping
