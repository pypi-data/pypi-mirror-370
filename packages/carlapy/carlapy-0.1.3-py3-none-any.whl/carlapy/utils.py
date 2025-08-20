import functools
import sys
import os
import fcntl
from typing import Callable

def safe_invoke() -> Callable:
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except RuntimeError as e:
                print(e)
                return None
        return wrapper
    return decorator

def set_stdout_nonblocking():
    fd = sys.stdout.fileno()
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    finally:
        pass
