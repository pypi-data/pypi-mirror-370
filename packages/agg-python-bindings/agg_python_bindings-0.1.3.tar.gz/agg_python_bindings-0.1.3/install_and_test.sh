echo "Building and installing wheel..."
uv pip install .
# continue only if the exit code is zero
if [ "$?" -eq "0" ]; then
    echo "Testing bindings..."
    python3 test_bindings.py
else
    echo "Installation failed"
    echo "Aborting test"
fi