from io import StringIO


class LoggingWrapper:
    def __init__(self, buffer: StringIO, prefix: str = None):
        self.buffer = buffer
        self.prefix = prefix or ""

    def write(self, message):
        if message.strip():
            self.buffer.write(f"{self.prefix}{message}\n")

    def flush(self):
        if hasattr(self.buffer, 'flush'):
            self.buffer.flush()
