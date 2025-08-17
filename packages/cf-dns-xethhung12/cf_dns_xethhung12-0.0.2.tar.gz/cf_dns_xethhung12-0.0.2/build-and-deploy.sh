BASEDIR=$(dirname $0)
pushd $BASEDIR
./build.sh
twine upload dist/*
popd