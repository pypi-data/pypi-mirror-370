pip3 install build setuptools-scm

pip3 install black!=23.1.0

black --check ./ut_com
pipreqs --force --ignore .mypy_cache --mode gt .
mypy ./ut_com

ruff --clean 
ruff --fix ./ut_com

pip3 install .
pip3 install build twine wheel setuptools-scm

cd ./docs; make man

python3 -m build --no-isolation --wheel --sdist
python3 -m build --wheel --sdist
twine check dist/*
twine upload dist/*
