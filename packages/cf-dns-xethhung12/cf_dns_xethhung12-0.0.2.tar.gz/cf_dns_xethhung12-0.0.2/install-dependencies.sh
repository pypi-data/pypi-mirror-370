BASEDIR=$(dirname $0)
pushd $BASEDIR
pip install -r dev-requirements.txt
pip install -r requirements.txt
popd