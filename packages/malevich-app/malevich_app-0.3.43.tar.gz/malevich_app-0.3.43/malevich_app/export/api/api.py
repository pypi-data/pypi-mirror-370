import json
import traceback
from typing import Dict, Any, List, Tuple, Optional
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    HTTP_405_METHOD_NOT_ALLOWED, HTTP_406_NOT_ACCEPTABLE
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
from malevich_app.docker_export.funcs import input_fun, processor_fun, output_fun, docker_mode
from malevich_app.export.abstract.abstract import (Init, InputCollections, AppFunctionsInfo, FunMetadata, InitRun,
                                                   LogsResult, LogsOperation, GetAppInfo, Run, Collection, Objects,
                                                   InitPipeline, RunPipeline, RunStream, Cancel,
                                                   PipelineStructureUpdate)
from malevich_app.export.jls.JuliusPipeline import JuliusPipeline
from malevich_app.export.jls.JuliusRegistry import JuliusRegistry
from malevich_app.export.kafka.KafkaHelper import KafkaHelper
from malevich_app.export.processes.main import logs_streaming_restart
from malevich_app.export.secondary.EntityException import EntityException
from malevich_app.export.secondary.LogHelper import log_error, log_debug
from malevich_app.export.secondary.ProfileMode import ProfileMode
from malevich_app.export.secondary.State import states, State
from malevich_app.export.secondary.fail_storage import FailStorage
from malevich_app.export.secondary.helpers import call_async_fun, get_schemes_names, save_collection_external, reverse_object_request
from malevich_app.export.secondary.init import init_fun, init_settings_main
from malevich_app.export.secondary.local_temp import DummyAppWrapper
from malevich_app.export.secondary.logger import *
from malevich_app.export.kafka.operations import init, consume
from malevich_app.export.secondary.logsStreaming import logs as get_logs
from malevich_app.export.secondary.zip import unzip_raw

if not C.IS_LOCAL:
    app = FastAPI()
    registry = JuliusRegistry()
    init_settings_main()
    with open("version") as f:
        version = f.readline()
else:
    app = DummyAppWrapper()
    registry = None # set it in local runner
    version = "local"
if not C.IS_EXTERNAL and not C.IS_LOCAL and C.ALLOW_KAFKA:
    init()


@app.get("/ping", status_code=HTTP_200_OK)
async def ping() -> str:
    return "pong"


@app.post("/logs", status_code=HTTP_200_OK)
async def logs(operation: LogsOperation, response: Response) -> LogsResult:
    state = states.get(operation.operationId)
    if state is None:
        response.status_code = HTTP_404_NOT_FOUND
        return LogsResult(data=f"wrong operationId {operation.operationId}")
    if C.LOGS_STREAMING:
        await logs_streaming_restart()
        return LogsResult()
    else:
        return get_logs(state, operation.runId)


@app.post("/app_info", status_code=HTTP_200_OK)
async def app_functions_info(info: GetAppInfo, response: Response) -> AppFunctionsInfo:
    try:
        registry.info.version = version
        return registry.info
    except:
        response.status_code = HTTP_400_BAD_REQUEST
        return AppFunctionsInfo(logs=traceback.format_exc(), version=version)


async def single_put(j_app, schemes_names: List[Optional[Tuple[Optional[str], ...]]]) -> Tuple[bool, List[Optional[Tuple[Optional[str], ...]]], Dict[str, Any]]:
    log_debug("PROCESSOR", processor_logger)
    ok, schemes_names_temp, res = await call_async_fun(lambda: processor_fun(j_app, processor_logger), processor_logger, j_app.debug_mode, j_app.logs_buffer)
    schemes_names.extend(schemes_names_temp)
    if ok and not j_app.is_stream():
        log_debug("OUTPUT", output_logger)
        ok, schemes_names_temp, res = await call_async_fun(lambda: output_fun(j_app, output_logger), output_logger, j_app.debug_mode, j_app.logs_buffer)
        schemes_names.extend(schemes_names_temp)
    return ok, schemes_names, res


@app.post("/input", status_code=HTTP_200_OK)
async def input_put(collections: InputCollections, response: Response) -> Dict[str, Any]:
    state = states.get(collections.operationId)
    if state is None:
        log_error(f"/input wrong operationId {collections.operationId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    log_debug("INPUT", input_logger)

    j_app = state.j_apps.get(collections.runId)
    if j_app is None:
        state.logs_buffer.write(f"/input wrong runId {collections.runId}\n")
        log_error(f"/input wrong runId {collections.runId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    j_app.set_index(collections.index)
    ok, schemes_names, res = await call_async_fun(lambda: input_fun(j_app, collections.data, input_logger), input_logger, j_app.debug_mode, j_app.logs_buffer)
    if ok and collections.singleRequest:
        ok, schemes_names, res = await single_put(j_app, schemes_names)
    if not ok:
        response.status_code = HTTP_400_BAD_REQUEST
    return {**res, "logs": read_logs(logfile), "schemesNames": get_schemes_names(schemes_names)}


@app.post("/processor", status_code=HTTP_200_OK)
async def processor_put(metadata: FunMetadata, response: Response) -> Dict[str, Any]:
    state = states.get(metadata.operationId)
    if state is None:
        log_error(f"/processor wrong operationId {metadata.operationId}", processor_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    log_debug("PROCESSOR", processor_logger)
    j_app = state.j_apps.get(metadata.runId)
    if j_app is None:
        state.logs_buffer.write(f"/processor wrong runId {metadata.runId}\n")
        log_error(f"/processor wrong runId {metadata.runId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    ok, schemes_names, res = await call_async_fun(lambda: processor_fun(j_app, processor_logger), processor_logger, j_app.debug_mode, j_app.logs_buffer)
    if not ok:
        response.status_code = HTTP_400_BAD_REQUEST
    return {**res, "logs": read_logs(logfile), "schemesNames": get_schemes_names(schemes_names)}


@app.post("/output", status_code=HTTP_200_OK)
async def output_put(metadata: FunMetadata, response: Response) -> Dict[str, Any]:
    state = states.get(metadata.operationId)
    if state is None:
        log_error(f"/output wrong operationId {metadata.operationId}", output_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    log_debug("OUTPUT", output_logger)
    j_app = state.j_apps.get(metadata.runId)
    if j_app is None:
        state.logs_buffer.write(f"/output wrong runId {metadata.runId}\n")
        log_error(f"/output wrong runId {metadata.runId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    if j_app.is_stream():
        state.logs_buffer.write(f"/output for stream runId {metadata.runId}\n")
        log_error(f"/output for stream runId {metadata.runId}", input_logger)
        response.status_code = HTTP_400_BAD_REQUEST
        return {}
    ok, schemes_names, res = await call_async_fun(lambda: output_fun(j_app, output_logger), output_logger, j_app.debug_mode, j_app.logs_buffer)
    if not ok:
        response.status_code = HTTP_400_BAD_REQUEST
    return {**res, "logs": read_logs(logfile), "schemesNames": get_schemes_names(schemes_names)}


@app.post("/init/pipeline", status_code=HTTP_200_OK)
async def init_pipeline(init: InitPipeline, response: Response) -> Dict[str, Any]:
    state = states.get(init.operationId)
    if state is not None:
        state.logs_buffer.write(f"/init/pipeline wrong: pipeline already inited, operationId {init.operationId}\n")
        log_error(f"/init/pipeline wrong: pipeline already inited, operationId {init.operationId}")
        response.status_code = HTTP_400_BAD_REQUEST
        data = state.logs_buffer.getvalue()
        return {"mode": docker_mode, "data": data, "inputCollections": []}

    try:
        state = State(init.operationId, init.schemesNames)
        states[init.operationId] = state
        init.pipeline.fix(init.index)
        fail_storage = FailStorage(os.path.join(C.COLLECTIONS_OBJ_PATH(init.login), C.FAILS_DIR)) if init.saveFails else None
        j_pipeline = JuliusPipeline(init, registry, state.logs_buffer, state.pauses, fail_storage=fail_storage)
        state.pipeline = j_pipeline
        state.schemes_names.update(j_pipeline.scheme_aliases())
        j_pipeline.set_exist_schemes(None, state.schemes_names)
        await registry.update_schemes_pipeline(init.operationId)
    except BaseException as ex:
        log_error("init pipeline failed")
        response.status_code = HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST
        if state is not None:
            state.logs_buffer.write(f"{traceback.format_exc()}\n")
            data = state.logs_buffer.getvalue()
        else:
            data = traceback.format_exc()
        states.pop(init.operationId, None)
        return {"mode": docker_mode, "data": data, "inputCollections": []}

    if not await j_pipeline.init():
        state.logs_buffer.write("init failed\n")
        log_error("init failed")
        response.status_code = HTTP_400_BAD_REQUEST
        data = state.logs_buffer.getvalue()
        j_app_data, j_app_logs_data = j_pipeline.logs()
        states.pop(init.operationId, None)
        return {"mode": docker_mode, "data": data, "logs": json.dumps(j_app_data), "userLogs": json.dumps(j_app_logs_data), "inputCollections": []}

    await registry.save_schemes(init.operationId)

    if C.ALLOW_KAFKA:
        await consume()

    j_app_data, j_app_logs_data = j_pipeline.logs(clear=False)
    return {"mode": docker_mode, "logs": json.dumps(j_app_data), "userLogs": json.dumps(j_app_logs_data), "inputCollections": j_pipeline.get_input_collections(raises=False)}


@app.post("/init_run/pipeline", status_code=HTTP_204_NO_CONTENT)
async def init_run_pipeline(init: InitRun):
    state = states.get(init.operationId)
    if state is None:
        log_error(f"/init_run/pipeline wrong operationId {init.operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)
    if state.pipeline is None:
        state.logs_buffer.write("error: init_run pipeline failed before, can't run\n")
        log_error("init_run pipeline failed before, can't run")
        return Response(status_code=HTTP_405_METHOD_NOT_ALLOWED)
    try:
        if not await state.pipeline.init_run(init):
            state.pauses.pop(init.runId, None)
            state.logs_buffer.write("error: init_run pipeline failed\n")
            log_error("init_run pipeline failed")
            j_app_data, j_app_logs_data = state.pipeline.logs()
            if len(j_app_data) > 0:
                state.logs_buffer.write(json.dumps(j_app_data))
            if len(j_app_logs_data) > 0:
                state.logs_buffer.write(json.dumps(j_app_logs_data))
            return Response(status_code=HTTP_400_BAD_REQUEST)
        state.pipeline.set_exist_schemes(init.runId, state.schemes_names)
    except BaseException as ex:
        state.pauses.pop(init.runId, None)
        state.logs_buffer.write(f"error init app: {traceback.format_exc()}\n")
        j_app_data, j_app_logs_data = state.pipeline.logs()
        if len(j_app_data) > 0:
            state.logs_buffer.write(json.dumps(j_app_data))
        if len(j_app_logs_data) > 0:
            state.logs_buffer.write(json.dumps(j_app_logs_data))
        return Response(status_code=HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST)

    if init.kafkaInitRun is not None:
        try:
            state.pipeline.set_for_kafka(init.runId)
        except BaseException as ex:
            state.pauses.pop(init.runId, None)
            state.logs_buffer.write("error: set kafka for app failed\n")
            state.logs_buffer.write(f"{traceback.format_exc()}\n")
            j_app_data, j_app_logs_data = state.pipeline.logs()
            if len(j_app_data) > 0:
                state.logs_buffer.write(json.dumps(j_app_data))
            if len(j_app_logs_data) > 0:
                state.logs_buffer.write(json.dumps(j_app_logs_data))
            log_error(traceback.format_exc())
            return Response(status_code=HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/run/pipeline", status_code=HTTP_200_OK)
async def run_pipeline(run: RunPipeline, response: Response) -> Dict[str, Any]:
    state = states.get(run.operationId)
    if state is None:
        log_error(f"/run/pipeline wrong operationId {run.operationId}", pipeline_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}

    if not state.pipeline.exist_run(run.runId):
        state.logs_buffer.write(f"/run/pipeline wrong runId {run.runId}\n")
        log_error(f"/run/pipeline wrong runId {run.runId}", pipeline_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}

    try:
        ok = await state.pipeline.run(run.runId, run.iteration, run.bindId, run.data, run.conditions, run.structureUpdate or PipelineStructureUpdate(), run.bindIdsDependencies)
        if not ok:
            response.status_code = HTTP_400_BAD_REQUEST
    except BaseException as ex:
        state.logs_buffer.write(f"{traceback.format_exc()}\n")
        response.status_code = HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST
    return {"logs": read_logs(logfile), "schemesNames": []}  # FIXME set schemesNames


@app.post("/init", status_code=HTTP_200_OK)
async def init_put(init: Init, response: Response) -> Dict[str, Any]:
    state = states.get(init.operationId)
    if state is not None:
        state.logs_buffer.write(f"/init wrong: app already inited, operationId {init.operationId}\n")
        log_error(f"/init wrong: app already inited, operationId {init.operationId}")
        response.status_code = HTTP_400_BAD_REQUEST
        data = state.logs_buffer.getvalue()
        return {"mode": docker_mode, "data": data, "inputCollections": []}
    state = State(init.operationId, init.schemesNames, init.scale, app=init.app, is_init_app=init.isInitApp)
    states[init.operationId] = state

    try:
        task_id = init.taskId if init.taskId != "" else None
        j_app = await init_fun(init, mode="init", operation_id=init.operationId, app_id=init.app.appId, task_id=task_id, extra_collections_from=init.app.extraCollectionsFrom)
    except BaseException as ex:
        log_error("init_fun failed")
        response.status_code = HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST
        data = state.logs_buffer.getvalue()
        j_app_data = traceback.format_exc()
        states.pop(init.operationId, None)
        return {"mode": docker_mode, "data": data, "logs": j_app_data, "inputCollections": []}
    j_app.debug_mode = init.debugMode
    j_app.dag_host_port = C.DAG_HOST_PORT(init.dagHost)
    j_app.run_id = "prepare"
    j_app.profile_mode = ProfileMode.from_str(init.profileMode)
    j_app.secret = init.secret
    j_app._single_pod = init.singlePod
    j_app.continue_after_processor = init.continueAfterProcessor
    j_app._login = init.login
    j_app.set_context()
    if not await j_app.init_all():
        j_app.logs_buffer.write("init_all failed\n")
        log_error("init_all failed")
        response.status_code = HTTP_400_BAD_REQUEST
        data = state.logs_buffer.getvalue()
        j_app_data = j_app.logs_buffer.getvalue()
        j_app_logs_data = j_app._context._logs(clear=False)
        states.pop(init.operationId, None)
        return {"mode": docker_mode, "data": data, "logs": j_app_data, "userLogs": j_app_logs_data, "inputCollections": []}

    state.logs_buffer.write(j_app.logs_buffer.getvalue())
    j_app.logs_buffer.truncate(0)
    j_app.logs_buffer.seek(0)

    state.base_j_app = j_app

    await registry.save_schemes(init.operationId)

    if C.ALLOW_KAFKA:
        await consume()
    return {"mode": docker_mode, "inputCollections": j_app.get_input_collections(raises=False)}


@app.post("/init_run", status_code=HTTP_204_NO_CONTENT)
async def init_run(init: InitRun):
    state = states.get(init.operationId)
    if state is None:
        log_error(f"/init_run wrong operationId {init.operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)
    if init.runId in state.j_apps:
        state.logs_buffer.write(f"error: app with runId={init.runId} already runned\n")
        log_error(f"app with runId={init.runId} already runned")
        return Response(status_code=HTTP_405_METHOD_NOT_ALLOWED)
    if state.base_j_app is None:
        state.logs_buffer.write("error: init app failed before, can't run\n")
        log_error("init app failed before, can't run")
        return Response(status_code=HTTP_405_METHOD_NOT_ALLOWED)
    try:
        j_app = await init_fun(init, mode="run", base_j_app=state.base_j_app)   # FIXME optimize, not reimport
        j_app.debug_mode = init.debugMode
        j_app.dag_host_port = C.DAG_HOST_PORT(init.dagHost)
        j_app.run_id = init.runId
        j_app.profile_mode = ProfileMode.from_str(init.profileMode)
        j_app._operation_id = init.operationId
        if init.kafkaInitRun is not None:
            j_app.kafka_helper = KafkaHelper(init.kafkaInitRun, j_app)
        j_app.set_context()
        pauses = state.pauses.get(init.runId)
        if pauses is None:
            pauses = {}
            state.pauses[init.runId] = pauses
        j_app._set_pauses(pauses)
    except BaseException as ex:
        state.logs_buffer.write(f"error init app: {traceback.format_exc()}\n")
        log_error(f"init app error: {traceback.format_exc()}")
        return Response(status_code=HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST)
    if not await j_app.init_all():
        state.pauses.pop(init.runId, None)
        state.logs_buffer.write("error: init_all failed\n")
        state.logs_buffer.write(j_app.logs_buffer.getvalue())
        state.logs_buffer.write(j_app._context._logs(clear=False))
        log_error("init_all failed")
        return Response(status_code=HTTP_400_BAD_REQUEST)
    if init.kafkaInitRun is not None:
        try:
            j_app.set_for_kafka()
        except BaseException as ex:
            state.pauses.pop(init.runId, None)
            state.logs_buffer.write("error: set kafka for app failed\n")
            state.logs_buffer.write(f"{traceback.format_exc()}\n")
            state.logs_buffer.write(j_app.logs_buffer.getvalue())
            state.logs_buffer.write(j_app._context._logs(clear=False))
            log_error(traceback.format_exc())
            return Response(status_code=HTTP_406_NOT_ACCEPTABLE if isinstance(ex, EntityException) else HTTP_400_BAD_REQUEST)
    state.j_apps[init.runId] = j_app
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/run", status_code=HTTP_200_OK)
async def run(collections: Run, response: Response) -> Dict[str, Any]:
    state = states.get(collections.operationId)
    if state is None:
        log_error(f"/run wrong operationId {collections.operationId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}

    j_app = state.j_apps.get(collections.runId)
    if j_app is None:
        state.logs_buffer.write(f"/run wrong runId {collections.runId}\n")
        log_error(f"/run wrong runId {collections.runId}", input_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}
    j_app.set_index(collections.index)

    log_debug("INPUT", input_logger)
    ok, schemes_names, res = await call_async_fun(lambda: input_fun(j_app, collections.data, input_logger),
                                                  input_logger, j_app.debug_mode, j_app.logs_buffer)
    if ok:
        ok, schemes_names, res = await single_put(j_app, schemes_names)
    if not ok:
        response.status_code = HTTP_400_BAD_REQUEST
    return {**res, "logs": read_logs(logfile), "schemesNames": get_schemes_names(schemes_names)}


@app.post("/stream", status_code=HTTP_200_OK)
async def stream(run: RunStream, response: Response):
    state = states.get(run.operationId)
    if state is None:
        log_error(f"/stream wrong operationId {run.operationId}", pipeline_logger)
        response.status_code = HTTP_404_NOT_FOUND
        return {}

    if run.bindId != "":    # pipeline
        if not state.pipeline.exist_run(run.runId):
            state.logs_buffer.write(f"/stream wrong runId {run.runId}\n")
            log_error(f"/stream wrong runId {run.runId}", pipeline_logger)
            response.status_code = HTTP_404_NOT_FOUND
            return {}
        generate_data = state.pipeline.stream(run.runId, run.bindId)
    else:
        j_app = state.j_apps.get(run.runId)
        if j_app is None:
            state.logs_buffer.write(f"/stream wrong runId {run.runId}\n")
            log_error(f"/stream wrong runId {run.runId}", processor_logger)
            response.status_code = HTTP_404_NOT_FOUND
            return {}
        generate_data = j_app.stream
    if generate_data is None:
        response.status_code = HTTP_400_BAD_REQUEST
        return {}

    return StreamingResponse(
        generate_data(),
        media_type="application/json",
    )


@app.post("/finish", status_code=HTTP_204_NO_CONTENT)
async def finish(metadata: FunMetadata):    # TODO stop all running
    state = states.get(metadata.operationId)
    if state is None:
        log_error(f"/finish wrong operationId {metadata.operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    if metadata.runId is None:
        if state.pipeline is None:
            for j_app in state.j_apps.values():
                j_app.cancel()
        else:
            state.pipeline.cancel()
        states.pop(metadata.operationId, None)
        return Response(status_code=HTTP_204_NO_CONTENT)

    if state.pipeline is None:
        state.j_apps.pop(metadata.runId, None)      # it could fail at the init
        state.pauses.pop(metadata.runId, None)
    else:
        state.pipeline.delete_run(metadata.runId)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/collection", status_code=HTTP_204_NO_CONTENT)
async def put_collection(collection: Collection):
    if collection.operationId not in states:
        log_error(f"/collection wrong operationId {collection.operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    save_collection_external(collection)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/objects", status_code=HTTP_204_NO_CONTENT)
async def put_objects(operationId: str, runId: Optional[str] = None, asset: bool = False, request: Request = None):
    if operationId is None:
        return Response(status_code=HTTP_405_METHOD_NOT_ALLOWED)

    state = states.get(operationId)
    if state is None:
        log_error(f"/objects wrong operationId {operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    if runId is not None:
        j_app = state.pipeline.any_run_japp(runId) or state.j_apps.get(runId)
        if j_app is None:
            state.logs_buffer.write(f"/objects wrong runId {runId}\n")
            log_error(f"/objects wrong runId {runId} (operationId={operationId})")
            return Response(status_code=HTTP_404_NOT_FOUND)
        logs_buffer = j_app.logs_buffer
    else:
        logs_buffer = state.logs_buffer

    raw_data: bytes = await request.body()
    if not unzip_raw(raw_data, operationId, runId, asset, logs_buffer, login=state.base_j_app._login if asset else None):
        return Response(status_code=HTTP_400_BAD_REQUEST)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/objects/reverse", status_code=HTTP_204_NO_CONTENT)
async def get_objects(objects: Objects):
    state = states.get(objects.operationId)
    if state is None:
        log_error(f"/objects/reverse wrong operationId {objects.operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    if objects.runId is not None:
        j_app = state.pipeline.any_run_japp(objects.runId) or state.j_apps.get(objects.runId)
        if j_app is None:
            state.logs_buffer.write(f"/objects/reverse wrong runId {objects.runId}\n")
            log_error(f"/objects/reverse wrong runId {objects.runId} (operationId={objects.operationId})")
            return Response(status_code=HTTP_404_NOT_FOUND)
        logs_buffer = j_app.logs_buffer
    else:
        logs_buffer = state.logs_buffer
    if not await reverse_object_request(objects, state.base_j_app.dag_host_port, logs_buffer):
        return Response(status_code=HTTP_400_BAD_REQUEST)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/continue/{operationId}/{runId}/{id}", status_code=HTTP_204_NO_CONTENT)
async def continue_(operationId: str, runId: str, id: str, request: Request):
    state = states.get(operationId)
    if state is None:
        log_error(f"/continue wrong operationId {operationId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    pauses = state.pauses.get(runId)
    if pauses is None:
        state.logs_buffer.write(f"/continue wrong runId {runId}\n")
        log_error(f"/continue wrong runId {runId}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    fut = pauses.pop(id, None)
    if fut is None:
        state.logs_buffer.write(f"/continue wrong id {id}\n")
        log_error(f"/continue wrong id {id}")
        return Response(status_code=HTTP_404_NOT_FOUND)

    fut.set_result(await request.body())
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.post("/cancel", status_code=HTTP_204_NO_CONTENT)
async def cancel(data: Cancel):
    for state in states.values():
        if state.pipeline is None:
            for j_app in state.j_apps.values():
                j_app.cancel()
        else:
            state.pipeline.cancel(delete=False)
            state.pipeline.reset_hash(data.hash)
    return Response(status_code=HTTP_204_NO_CONTENT)
