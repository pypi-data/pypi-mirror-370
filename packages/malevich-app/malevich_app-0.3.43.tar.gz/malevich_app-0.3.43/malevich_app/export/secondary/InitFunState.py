import asyncio
from datetime import datetime
from typing import Optional
from malevich_app.export.jls.df import get_fun_info
from malevich_app.export.jls.helpers import is_async, run_func
from malevich_app.export.secondary.const import CONTEXT, START, END
from malevich_app.export.secondary.redirect import redirect_out


class InitFunError(Exception):
    def __init__(self, fun_id: str):
        super().__init__(fun_id)
        self.fun_id = fun_id


class InitFunState:
    def __init__(self, j_app, init_fun: callable, id: str, tl: Optional[int], cpu_bound: bool):
        self.j_app = j_app
        self.fun = init_fun
        self.fun_id = id
        self.tl = tl
        self.cpu_bound = cpu_bound
        self.with_context = False

        fun_info = get_fun_info(init_fun)[0]
        if len(fun_info) != 0:
            assert len(fun_info) == 1 and fun_info[0][1] == CONTEXT, f"\"init\" must have no parameters or only Context (app id={j_app.app_id}, id={self.fun_id})"
            self.with_context = True

    def __init_fun(self, *args):
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {START}, {datetime.now()}\n")
        res = self.fun(*args)
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {END}, {datetime.now()}\n")
        return res

    async def __async_init_fun(self, *args):
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {START}, {datetime.now()}\n")
        res = await self.fun(*args)
        if self.j_app.profile_mode is not None and self.j_app.profile_mode.time:
            self.j_app.logs_buffer.write(f"{self.fun_id}, {END}, {datetime.now()}\n")
        return res

    async def run(self):
        args = [self.j_app._get_context(self.fun_id)] if self.with_context else []

        with redirect_out(self.j_app.logs_buffer):
            try:
                if is_async(self.fun):
                    await asyncio.wait_for(self.__async_init_fun(*args), timeout=self.tl)
                else:
                    await asyncio.wait_for(run_func(self.__init_fun, *args, cpu_bound=self.cpu_bound, logs_buffer=self.j_app.logs_buffer), timeout=self.tl)
            except BaseException as e:
                raise InitFunError(self.fun_id) from e
