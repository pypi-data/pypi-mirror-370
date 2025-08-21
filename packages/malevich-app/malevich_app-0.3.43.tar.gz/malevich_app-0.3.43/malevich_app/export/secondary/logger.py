import logging
import os
from datetime import datetime
import malevich_app.export.secondary.const as C

logfile = "logfile.log"
if os.environ.get("LOGS") is None:
    logging.basicConfig(filename=logfile,
                        filemode="a",
                        format='%(asctime)s.%(msecs)03dZ %(name)s %(levelname)s %(message)s',
                        datefmt=C.TIME_FORMAT,
                        level=logging.INFO)
else:
    logging.basicConfig()

input_logger = logging.getLogger("input")
processor_logger = logging.getLogger("processor")
output_logger = logging.getLogger("output")
condition_logger = logging.getLogger("condition")
pipeline_logger = logging.getLogger("pipeline")
context_logger = logging.getLogger("context")


def read_logs(filename: str):
    res = []
    with open(filename, 'r+') as f:
        f.seek(0)
        for line in f.read().splitlines():
            try:
                timestamp, component, level, row = line.split(maxsplit=3)
                datetime.strptime(timestamp[:-5], C.TIME_FORMAT)    # failed for wrong logs
                res.append({
                    "timestamp": timestamp,
                    "component": component,
                    "level": level,
                    "row": row
                })
            except:     # FIXME
                pass
        f.truncate(0)
    return res
