# viso-sdk-python

**viso-sdk-python** is a utility for [viso.ai](https://viso.ai) containers.

## Installation

Use `pip` to install the latest stable version of **viso-sdk-python**:

```shell
pip install viso-sdk-python
```


## Build
```shell
python3 -m pip install -e .
python3 setup.py sdist bdist_wheel

# pip3 install setuptools-cythonize
# pip3 install setuptools
# pip3 install --upgrade pip
```

```shell
- remove build files before pushing
cd viso_sdk
find . -type f -name "*.c" -delete
find . -type f -name "*.so" -delete
```


## Build sphinx document
```shell
# setup dependencies for sphinx autodoc extensions
pip3 install -r requirements-docs.txt

# 
mkdir docs
cd docs

# run script for generating autodoc 
sphinx-apidoc -e -P -f -o source/ ../viso_sdk
make html

# execute html page
cd docs/_build/index.html
```