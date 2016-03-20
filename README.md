Numpy Allocation Tracking
=========================

The numpy git repo includes a useful [`allocation_tracking`][allocation_tracking] package in the `tools` directory, but numpy doesn't install it by default.  This repo includes a conda recipe to install that package, along with some extra utilities and decorators.

**A Tiny Note:** The `allocation_tracking` module's `setup.py` would normally install `alloc_hook` into the global namespace, but this package installs everything into the namespace `numpy_allocation_tracking`.

[allocation_tracking]: https://github.com/numpy/numpy/tree/master/tools/allocation_tracking

Installation
------------

    conda install -c ilastik numpy-allocation-tracking

Build it yourself
-----------------

To build this recipe yourself for say, numpy 1.9:

    conda build --numpy=1.9 conda-recipe

**Note:** If you make any changes to this repo, you must commit them before building the recipe.  Uncommitted changes are not included in the build.

Example Usage
-------------

```python

from numpy_allocation_tracking.decorators import assert_mem_usage_factor

# If this function uses more RAM than 2x the size
# of input_array, raise an error.
# (Useful for testing purposes, not in production code.)
@assert_mem_usage_factor(2.0)
def dumb_function(input_array, x, y, z):
    return x * (input_array + y + z)

result = dumb_function( np.ones((100,100)), 10, 20, 30 )
```
