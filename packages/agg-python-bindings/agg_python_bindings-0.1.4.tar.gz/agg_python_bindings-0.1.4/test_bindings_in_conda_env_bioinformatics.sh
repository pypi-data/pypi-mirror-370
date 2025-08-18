CONDA_ENV=bioinformatics
TEST_SCRIPT=test_bindings.py

echo "Test script: $TEST_SCRIPT"
echo "Testing bindings in conda environment $CONDA_ENV"

conda run -n $CONDA_ENV --no-capture-output python $TEST_SCRIPT