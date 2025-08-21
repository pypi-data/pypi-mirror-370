import json
import uuid
import aiohttp
from typing import Optional, Dict, Any, Union, List
import malevich_app.export.secondary.const as C
from malevich_app.export.abstract.abstract import WSMessage
from malevich_app.ws.EventWaiter import waiter
from malevich_app.ws.utils import ws_send


async def _ws(operation_id: str, operation: str, data: Optional[str] = None) -> Optional[Dict[str, Any]]:
    assert operation_id is not None, "operation_id not set for ws communication"
    operation = operation.removeprefix("/")
    id = str(uuid.uuid4())
    msg = WSMessage(
        operationId=operation_id,
        payload=data,
        error=None,
        operation=operation,
        id=id,
    )
    await ws_send(msg.model_dump_json())
    C.WS_SEND.append(msg)
    data, err = await waiter.wait(id, operation)
    if err is not None:
        raise Exception(err)
    if data is not None:
        data = json.loads(data)
    return data


async def send_post_dag(values: Union[str, bytes], operation: str, *, raw_res: bool = False, headers: Dict[str, str] = None, operation_id: Optional[str] = None) -> Optional[Union[Dict[str, Any], List[str], bytes]]:
    if C.WS is None:
        async with aiohttp.ClientSession(timeout=C.AIOHTTP_TIMEOUT) as session:
            if headers is None:
                headers = C.DEFAULT_HEADERS
            async with session.post(operation, data=values, headers=headers) as response:
                response.raise_for_status()
                if response.status == 204:
                    return None
                if raw_res:
                    return await response.read()
                return await response.json()
    else:
        return await _ws(operation_id, operation, values)


async def send_delete_dag(values: str, operation: str, operation_id: Optional[str] = None):
    if C.WS is None:
        async with aiohttp.ClientSession(timeout=C.AIOHTTP_TIMEOUT) as session:
            async with session.delete(operation, data=values, headers=C.DEFAULT_HEADERS) as response:
                response.raise_for_status()
    else:
        await _ws(operation_id, operation, values)
