import time
import inspect
from pathlib import Path

PREV_TIME = time.time()


def measure_import_time():
    # writes time elapsed between two calls

    global PREV_TIME
    frame = inspect.currentframe().f_back
    line_number = frame.f_lineno
    filename = frame.f_globals["__file__"]

    cur_time = time.time()
    elapsed_time = cur_time - PREV_TIME
    PREV_TIME = cur_time

    print(f"Line {line_number} in {Path(filename).name}: Time from last call: {elapsed_time:.2f} sec")
