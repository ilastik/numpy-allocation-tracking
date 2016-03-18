Numpy Allocation Tracking
=========================

The numpy git repo includes a useful [`allocation_tracking`][allocation_tracking] package in the `tools` directory, but numpy doesn't install it by default.  This repo includes a conda recipe to install that package, along with some extra utilities and decorators.

**A Tiny Note:** The `allocation_tracking` module's `setup.py` would normally install `alloc_hook` into the global namespace, but this package installs everything into the namespace `numpy_allocation_tracking`.

[allocation_tracking]: https://github.com/numpy/numpy/tree/master/tools/allocation_tracking

Installation
------------

    conda install -c ilastik numpy_allocation_tracking

Build it yourself
-----------------

To build this recipe yourself for say, numpy 1.9:

    conda build --numpy=1.9 conda-recipe

**Note:** If you make any changes to this repo, you must commit them before building the recipe.  Uncommitted changes are not included in the build.
