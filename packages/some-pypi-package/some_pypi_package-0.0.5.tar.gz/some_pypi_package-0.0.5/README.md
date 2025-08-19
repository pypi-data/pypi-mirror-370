# some_pypi_package

A simple example Python package.

https://www.youtube.com/watch?v=Kz6IlDCyOUY

Make sure you change the build version in setup.py

## UV Installation

```bash
pip install uv
uv build
```

## Standard Installation

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
pip install some_pypi_package
python setup.py sdist bdist_wheel
```

## Register
Open a pypi account here: https://pypi.org/

## Publish
twine upload -u <username> -p <password> dist/*
