import sys
from io import StringIO
from contextlib import AbstractContextManager
from malevich_app.export.secondary.LoggingWrapper import LoggingWrapper


class _DualStreamRedirect(AbstractContextManager):
    def __init__(self, buffer: StringIO):
        self.buffer = buffer
        self._old_stdout = []
        self._old_stderr = []

    def __enter__(self):
        self._old_stdout.append(sys.stdout)
        sys.stdout = LoggingWrapper(self.buffer)
        self._old_stderr.append(sys.stderr)
        sys.stderr = LoggingWrapper(self.buffer, "stderr: ")
        return self.buffer

    def __exit__(self, exctype, excinst, exctb):
        sys.stdout = self._old_stdout.pop()
        sys.stderr = self._old_stderr.pop()


def redirect_out(buffer: StringIO):
    return _DualStreamRedirect(buffer)
