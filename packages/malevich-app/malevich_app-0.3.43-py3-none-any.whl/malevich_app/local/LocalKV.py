from typing import Any, Dict, Optional, List


class LocalKV:
    """simple local kv implementation for one run"""

    # FIXME non-identical behavior locally
    def __init__(self):
        self.__data: Dict[str, Dict[str, Any]] = {}
        pass

    def __key(self, operation_id: str, run_id: Optional[str]) -> str:
        return f"${operation_id}${run_id}$"

    def __subdata(self, operation_id: str, run_id: Optional[str]) -> Optional[Dict[str, Any]]:
        return self.__data.get(self.__key(operation_id, run_id))

    def get_bytes(self, operation_id: str, run_id: Optional[str], key: str) -> bytes:   # FIXME
        data = self.__subdata(operation_id, run_id)
        assert data is not None
        res = data.get(key)
        assert res is not None
        if isinstance(res, bytes):
            return res
        return bytes(res)

    def get(self, operation_id: str, run_id: Optional[str], keys: List[str]) -> Dict[str, Any]:
        data = self.__subdata(operation_id, run_id)
        if data is None:
            return {}

        res = {}
        for k in keys:
            v = data.get(k)
            if v is not None:
                res[k] = v
        return res

    def get_all(self, operation_id: str, run_id: Optional[str]) -> Dict[str, Any]:
        data = self.__subdata(operation_id, run_id)
        if data is None:
            return {}
        return data

    def update(self, operation_id: str, run_id: Optional[str], keys_values: Dict[str, Any]) -> None:
        key = self.__key(operation_id, run_id)
        data = self.__data.get(key)
        if data is None:
            data = {}
            self.__data[key] = data

        data.update(keys_values)

    def clear(self, operation_id: str, run_id: Optional[str]) -> None:
        key = self.__key(operation_id, run_id)
        self.__data.pop(key, None)
