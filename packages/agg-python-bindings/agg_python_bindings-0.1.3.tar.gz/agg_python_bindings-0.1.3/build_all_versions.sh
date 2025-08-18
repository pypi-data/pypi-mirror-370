# build source release
echo "Building source distribution"
maturin sdist

# list and build all possible python wheels

pyversions="python3.8 python3.9 python3.10 python3.11 python3.12"
for pyversion in $pyversions
do
    echo "Compiling wheel for $pyversion (release)"
    maturin build -i $pyversion --release
done

# optionally upload some wheels
echo "Use twine upload <wheel_path> to upload artifacts"
# twine upload target/wheels/*