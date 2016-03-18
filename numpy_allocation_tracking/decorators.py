from .track_allocations import AllocationTracker

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

