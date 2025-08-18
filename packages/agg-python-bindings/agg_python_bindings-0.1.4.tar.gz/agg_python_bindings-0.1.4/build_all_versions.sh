VERSION=$(cat Cargo.toml | grep version | head --lines 1 | awk -F '"' '{print $2}')

echo "Building version $VERSION"

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

# ask the user if they want to upload artifacts
read -p "Do you want to proceed? (yes/no) " yn

case $yn in 
	yes ) echo ok, we will proceed;;
	no ) echo exiting...;
		exit;;
	* ) echo invalid response;
		exit 1;;
esac

find target/wheels/ | grep $VERSION | xargs -Iabc twine upload abc