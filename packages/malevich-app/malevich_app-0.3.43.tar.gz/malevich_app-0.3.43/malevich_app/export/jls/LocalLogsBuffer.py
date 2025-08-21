import logging
from io import StringIO
from typing import Optional, Callable


class LocalLogsBuffer(StringIO):
    def __init__(self, logger_fun: Callable[[str, Optional[str], Optional[str], bool], logging.Logger], operation_id: str, run_id: Optional[str] = None, bind_id: Optional[str] = None, user_logs: bool = False):
        super().__init__()
        self.__logger_fun = logger_fun
        self.__operation_id = operation_id
        self.__run_id = run_id
        self.__bind_id = bind_id
        self.__user_logs = user_logs

        self.__logger = logger_fun(operation_id, run_id, bind_id, user_logs)

    def update_run_id(self, run_id: str):
        self.__run_id = run_id
        self.__logger = self.__logger_fun(self.__operation_id, run_id, self.__bind_id, self.__user_logs)

    @property
    def logger(self):
        return self.__logger

    def write(self, data: str, *args, **kwargs):
        super().write(data, *args, **kwargs)
        self.__logger.info(data.removesuffix("\n"))
