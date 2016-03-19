cd ${SRC_DIR}/numpy_allocation_tracking/tests
for f in $(ls *.py); do
    python $f
done
