# Download the numpy source repo
CONDA_PYTHON=$(conda info --root)/bin/python
"${CONDA_PYTHON}" "${RECIPE_DIR}/download-extra-sources.py"

# Read the numpy tag from git
# (We'll version this package according to the numpy version.)
cd numpy
NUMPY_GIT_DESCRIBE_TEXT=$(git describe --tags --long HEAD)
NUMPY_GIT_DESCRIBE_TAG=$(python -c    "from __future__ import print_function; print(\"${NUMPY_GIT_DESCRIBE_TEXT}\".rsplit(\"-\", 2)[0])") 
#NUMPY_GIT_DESCRIBE_NUMBER=$(python -c "from __future__ import print_function; print(\"${NUMPY_GIT_DESCRIBE_TEXT}\".rsplit(\"-\", 2)[1])") 
#NUMPY_GIT_DESCRIBE_HASH=$(python -c   "from __future__ import print_function; print(\"${NUMPY_GIT_DESCRIBE_TEXT}\".rsplit(\"-\", 2)[2])") 
cd -

cat << EOF > __conda_version__.txt
${NUMPY_GIT_DESCRIBE_TAG}
EOF

cat << EOF > __conda_buildstr__.txt
py${CONDA_PY}np${CONDA_NPY}_${PKG_BUILDNUM}_g${GIT_FULL_HASH:0:7}
EOF

# Build the alloc_hook extension module
cd numpy/tools/allocation_tracking
${PYTHON} setup.py build_ext

# Copy into a single directory
cp build/lib*/alloc_hook.so ${SRC_DIR}/numpy_allocation_tracking/
cp *.* ${SRC_DIR}/numpy_allocation_tracking/
rm ${SRC_DIR}/numpy_allocation_tracking/setup.py

# Install
cp -r ${SRC_DIR}/numpy_allocation_tracking "${PREFIX}/lib/python${PY_VER}/site-packages/"
