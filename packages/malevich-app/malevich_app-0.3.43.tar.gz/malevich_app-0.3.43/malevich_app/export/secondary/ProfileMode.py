import io
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
import pandas as pd
from malevich_app.export.jls.df import DFS, Sink
from malevich_app.export.secondary.LogHelper import log_warn
from malevich_app.export.secondary.const import DELIMITER, START, END


class ProfileMode(Enum):
    NO = "no"
    ALL = "all"
    TIME = "time"
    DF_INFO = "df_info"
    DF_SHOW = "df_show"

    @property
    def no(self) -> bool:
        return self == self.NO

    @property
    def time(self) -> bool:
        return self == self.TIME or self == self.ALL

    @property
    def df_info(self) -> bool:
        return self == self.DF_INFO or self == self.ALL

    @property
    def df_show(self) -> bool:
        return self == self.DF_SHOW or self == self.ALL

    @staticmethod
    def from_str(mode: Optional[str]):
        if mode is None:
            return ProfileMode.NO
        elif mode == ProfileMode.NO.value:
            return ProfileMode.NO
        elif mode == ProfileMode.ALL.value:
            return ProfileMode.ALL
        elif mode == ProfileMode.TIME.value:
            return ProfileMode.TIME
        elif mode == ProfileMode.DF_INFO.value:
            return ProfileMode.DF_INFO
        elif mode == ProfileMode.DF_SHOW.value:
            return ProfileMode.DF_SHOW
        else:
            log_warn("wrong profile mode")
            return ProfileMode.NO

    def __map_df(self, *args, fun: Callable[[pd.DataFrame], None], buffer: io.StringIO):
        first = True

        def iteration(arg):
            nonlocal first
            if not first:
                buffer.write(f"{DELIMITER}\n")
            else:
                first = False
            if isinstance(arg, pd.DataFrame):
                fun(arg)
            elif callable(arg):
                buffer.write(f"{arg.__qualname__}\n")
            else:
                buffer.write(f"{arg}\n")

        def __rec_iteration(args):
            for arg in args:
                if isinstance(arg, DFS) or isinstance(arg, Sink):
                    __rec_iteration(arg)
                else:
                    iteration(arg)
        __rec_iteration(args)

    def __run(self, *args, fun_id: str, mode: str = "", buffer: io.StringIO):
        if self.time:
            buffer.write(f"{fun_id}, {mode}, {datetime.now()}\n")
        mode = "" if mode == "" else f", {mode}"
        if self.df_info and len(args) > 0:
            buffer.write(f"----- df info ({fun_id}{mode}) -----\n")
            self.__map_df(*args, fun=lambda x: x.info(verbose=True, buf=buffer), buffer=buffer)
            buffer.write(f"----- df info ({fun_id}{mode}). -----\n")
        if self.df_show and len(args) > 0:
            buffer.write(f"----- df show ({fun_id}{mode}) -----\n")
            self.__map_df(*args, fun=lambda x: buffer.write(f"{x.head()}\n"), buffer=buffer)
            buffer.write(f"----- df show ({fun_id}{mode}). -----\n")

    def run_start(self, *args, fun_id: str, buffer: io.StringIO):
        if self.no:
            return
        self.__run(*args, fun_id=fun_id, mode=START, buffer=buffer)

    def run_end(self, *args, fun_id: str, buffer: io.StringIO):
        if self.no:
            return
        self.__run(*args, fun_id=fun_id, mode=END, buffer=buffer)
