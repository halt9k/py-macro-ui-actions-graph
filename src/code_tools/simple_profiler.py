import inspect
import time
from pathlib import Path

PREV_TIME = time.time()


def perfomance_timer(stage_name: str = None):
    # prints time elapsed from previous call

    global PREV_TIME
    frame = inspect.currentframe().f_back
    line_number = frame.f_lineno
    filename = frame.f_globals["__file__"]

    cur_time = time.time()
    elapsed_time = cur_time - PREV_TIME
    PREV_TIME = cur_time

    if stage_name:
        stage_name = f" stage {stage_name}"
    line_desc = f"Line {line_number} in {Path(filename).name} {stage_name}"
    print(f"{line_desc}: Time from last call: {elapsed_time:.2f} sec")
