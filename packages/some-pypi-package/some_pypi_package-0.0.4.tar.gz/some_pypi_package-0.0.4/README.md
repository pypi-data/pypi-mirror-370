# some_pypi_package

A simple example Python package.

https://www.youtube.com/watch?v=Kz6IlDCyOUY

## UV Installation

```bash
uv build
```

## Standard Installation

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
pip install some_pypi_package
```

## Build
python setup.py sdist bdist_wheel

## Publish
twine upload dist/*