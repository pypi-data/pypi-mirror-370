"""
Status: Experimental
"""
import functools
from threading import Lock as ThreadLock
from typing import Callable


def synchronized(func: Callable):
    """ Make the wrapped callable have one invocation at a time.

        Inspired by Java's "synchronized" keyword.
    """
    func.__syncable_thread_lock__ = ThreadLock()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with func.__syncable_thread_lock__:
            result = func(*args, **kwargs)

        reversed_stack = reversed(deferrable_deferred_stack)
        for op in reversed_stack:
            op()
        # end for

        return result
    # end wrapper