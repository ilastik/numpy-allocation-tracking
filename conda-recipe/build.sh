# Download the numpy source repo
CONDA_PYTHON=$(conda info --root)/bin/python
"${CONDA_PYTHON}" "${RECIPE_DIR}/download-extra-sources.py"

if [[ $(uname) == "Darwin" ]]; then
    export MACOSX_DEPLOYMENT_TARGET=10.7
fi

# Build the alloc_hook extension module
cd numpy/tools/allocation_tracking
${PYTHON} setup.py build_ext

# Copy into a single directory
cp build/lib*/alloc_hook*.so ${SRC_DIR}/numpy_allocation_tracking/
cp *.* ${SRC_DIR}/numpy_allocation_tracking/
rm ${SRC_DIR}/numpy_allocation_tracking/setup.py

# Install
cp -r ${SRC_DIR}/numpy_allocation_tracking "${PREFIX}/lib/python${PY_VER}/site-packages/"
