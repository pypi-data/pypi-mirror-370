import json
from typing import Optional
from malevich_app.export.abstract.abstract import LogsResult, LogsResults, LogsResultExtended
from malevich_app.export.request.dag_requests import send_post_dag
from malevich_app.export.secondary.State import states
from malevich_app.export.secondary.endpoints import STREAM_LOGS


def logs(state, run_id: Optional[str] = None):
    if state.pipeline is None:
        app_prints = {}
        app_logs = {}
        if run_id is None:
            for run_id, j_app in state.j_apps.items():
                app_prints[run_id] = j_app.logs_buffer.getvalue()
                j_app.logs_buffer.truncate(0)
                j_app.logs_buffer.seek(0)
                app_logs[run_id] = j_app._context._logs()
        else:
            j_app = state.j_apps.get(run_id)
            if j_app is None:
                app_prints[run_id] = "failed before"    # FIXME
            else:
                app_prints[run_id] = j_app.logs_buffer.getvalue()
                j_app.logs_buffer.truncate(0)
                j_app.logs_buffer.seek(0)
                app_logs[run_id] = j_app._context._logs()
    else:
        app_prints = {}
        app_logs = {}
        if run_id is None:
            for run_id in state.pipeline.runs():
                j_app_data, j_app_logs_data = state.pipeline.logs(run_id, clear=True)
                app_prints[run_id] = json.dumps(j_app_data)
                app_logs[run_id] = json.dumps(j_app_logs_data)
        else:
            if not state.pipeline.exist_run(run_id):
                app_prints[run_id] = json.dumps({"": "failed before"})     # FIXME
            else:
                j_app_data, j_app_logs_data = state.pipeline.logs(run_id, clear=True)
                app_prints[run_id] = json.dumps(j_app_data)
                app_logs[run_id] = json.dumps(j_app_logs_data)

    data = state.logs_buffer.getvalue()
    state.logs_buffer.truncate(0)
    state.logs_buffer.seek(0)
    return LogsResult(data=data, logs=app_prints, userLogs=app_logs)


async def logs_streaming_iteration():   # FIXME improve for pipeline
    dag_host_port_to_data = {}
    for operation_id, state in states.items():
        if state.pipeline is None:
            if len(state.j_apps) == 0 and state.logs_buffer.tell() == 0:
                continue
            base_j_app = state.base_j_app
            if base_j_app is None:
                continue

            dag_host_port = base_j_app.dag_host_port  # FIXME different dag_host_port for runs
            data = dag_host_port_to_data.get(dag_host_port)
            if data is None:
                data = {}
                dag_host_port_to_data[dag_host_port] = data
            state_logs = logs(state)
            if len(state_logs.data) > 0 or \
                    any(len(app_prints) > 0 for app_prints in state_logs.logs.values()) or \
                    any(len(app_logs) > 0 for app_logs in state_logs.userLogs.values()):
                data[operation_id] = LogsResultExtended(data=state_logs.data, logs=state_logs.logs,
                                                        userLogs=state_logs.userLogs,
                                                        taskId=base_j_app.task_id, appId=base_j_app.app_id,
                                                        index=base_j_app._context.scale_info[0])
        else:
            pipeline = state.pipeline
            dag_host_port = pipeline.dag_host_port  # FIXME different dag_host_port for runs
            data = dag_host_port_to_data.get(dag_host_port)
            if data is None:
                data = {}
                dag_host_port_to_data[dag_host_port] = data

            # FIXME copypaste
            state_logs = logs(state)
            if len(state_logs.data) > 0 or \
                    any(len(app_prints) > 0 for app_prints in state_logs.logs.values()) or \
                    any(len(app_logs) > 0 for app_logs in state_logs.userLogs.values()):
                data[operation_id] = LogsResultExtended(data=state_logs.data, logs=state_logs.logs,
                                                        userLogs=state_logs.userLogs,
                                                        taskId="", appId="", index=0)   # FIXME

    for dag_host_port, data in dag_host_port_to_data.items():
        if len(data) == 0:
            continue
        res = LogsResults(data=data)
        operation_id = list(data.keys())[0]
        await send_post_dag(res.model_dump_json(), STREAM_LOGS(dag_host_port), operation_id=operation_id)
