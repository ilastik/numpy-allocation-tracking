import numpy as np

from .track_allocations import AllocationTracker

import os
import functools
import logging
logger = logging.getLogger(__name__)

def track_max_alloc(func):
    """
    Decorator.
    
    Uses AllocationTracker from the numpy repo (in the tools directory)
    to track all numpy allocations in the given function.
    (You have to install the alloc_hook and track_allocations modules manually.)
    
    The high-water-mark of numpy memory allocations introduced by the function 
    will be saved as an attribute on the function itself, named 'max_array_usage'.
    You should examine it immediately after calling the function.
    (It will be overwritten the next time the function is called.)
    
    Example usage:
        >>> a = np.ones((1000,), dtype=np.uint8)
    
        >>> @track_max_alloc
        ... def f(a):
        ...     return a + a
    
        >>> b = f(a)
        >>> print f.max_array_usage
        1000

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.tracker = AllocationTracker()
        with wrapper.tracker:
            res = func(*args, **kwargs)
        overall_max = 0
        for idx, event in enumerate(wrapper.tracker.allocation_trace):
            overall_max = max(overall_max, event[5])
        wrapper.max_array_usage = overall_max
        return res
    wrapper.__wrapped__ = func # Emulate python 3 behavior of @functools.wraps
    return wrapper

def assert_mem_usage_factor(max_allowed_usage_factor=1.0, comparison_input_arg=0, memory_log_dir=None):
    """
    Returns a decorator.
    
    The decorator checks the memory usage of all numpy array allocations made by the decorated function.

    By default, the memory usage is compared to the size of the decorated function's first argument.
    Override via comparison_input_arg:
    - If comparison_input_arg is an int  N, compare with the Nth argument instead of the 0th.
    - If comparison_input_arg is a str, it is assumed to be a keyword arg to the function.
    - If comparison_input_arg is an ndarray, it is directly used for the comparison.

    If the memory usage exceeds some multiple of the compared data's size (as specified by max_allowed_usage_factor),
    then an assertion is raised, and an html log file of numpy allocations is written out.
    Set memory_log_dir to customize the location of the written log file.  (By default, it's written to the CWD.)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Pick an input argument to compare usage against.
            if isinstance(comparison_input_arg, int):
                input_data = args[comparison_input_arg]
            elif isinstance(comparison_input_arg, str):
                input_data = kwargs[comparison_input_arg]
            elif isinstance(comparison_input_arg, np.ndarray):
                input_data = comparison_input_arg
            assert isinstance(input_data, np.ndarray)
    
            func_name = func.__name__
            if isinstance(func, functools.partial):
                func_name = func.func.__name__
            
            memtracked_func = track_max_alloc(func)
            result = memtracked_func(*args, **kwargs)
    
            mem_usage_mb = memtracked_func.max_array_usage / 1e6
            mem_usage_factor = memtracked_func.max_array_usage / float(input_data.nbytes)
    
            logger.debug( "Memory usage factor of {}(): {:.1f}x".format(func.__name__, mem_usage_factor) )
        
            try:
                output_dir = memory_log_dir or os.getcwd()
                usage_log_path = os.path.join(output_dir, func.__name__ + '-allocation-log.html')
                assert mem_usage_factor <= max_allowed_usage_factor, \
                    "Max memory usage of '{}' was too high: {:.1f} MB ({:.1f}x of input)\n"\
                    "Writing mem_usage_log to {}\n"\
                    .format( func_name, mem_usage_mb, mem_usage_factor, usage_log_path )
            except AssertionError:
                memtracked_func.tracker.write_html(usage_log_path)
                raise
        
            return result

        wrapper.__wrapped__ = func # Emulate python 3 behavior of @functools.wraps
        return wrapper
    return decorator
