import sys
import threading
from collections import namedtuple


def run_in_thread(func, *args, **kwargs):
    result = None

    def thread_target():
        nonlocal result
        result = func(*args, **kwargs)

    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()
    return result


SizeTuple = namedtuple('SizeTuple', ('w', 'h'))


def check_py_version():
    if sys.version_info < (3, 7):
        print("This script uses @dataclasses and requires Python 3.7 or above")
        sys.exit(1)


check_py_version()
