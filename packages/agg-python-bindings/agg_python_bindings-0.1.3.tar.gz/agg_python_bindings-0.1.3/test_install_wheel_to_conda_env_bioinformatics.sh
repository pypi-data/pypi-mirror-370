CONDA_ENV=bioinformatics

# the wheel file built by maturin seems not having type annotations.
# however, the test code will work fine without annotations.
# let's install from source
# WHEEL_FILE=./target/wheels/agg_python_bindings-0.1.0-cp311-cp311-manylinux_2_34_x86_64.whl

echo "Wheel file: $WHEEL_FILE"
echo "Installing wheel to conda environment $CONDA_ENV"

# conda run -n $CONDA_ENV --no-capture-output pip install $WHEEL_FILE
conda run -n $CONDA_ENV --no-capture-output pip install .