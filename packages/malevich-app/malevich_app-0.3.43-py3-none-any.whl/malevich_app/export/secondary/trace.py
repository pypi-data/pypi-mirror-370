import sys
import traceback


def format_exc_skip(skip: int = 0, limit=None, chain=True):
    er_type, er, trace = sys.exc_info()
    trace_skip = trace
    for _ in range(skip):
        trace_skip = trace_skip.tb_next
        if trace_skip is None:
            break
    if trace_skip is None:
        trace_skip = trace
    return "".join(traceback.format_exception(er_type, er, trace_skip, limit=limit, chain=chain))
