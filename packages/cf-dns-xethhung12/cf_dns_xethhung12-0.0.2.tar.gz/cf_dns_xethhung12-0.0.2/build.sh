BASEDIR=$(dirname $0)
pushd $BASEDIR
rm -fr dist/*
python -m build
popd