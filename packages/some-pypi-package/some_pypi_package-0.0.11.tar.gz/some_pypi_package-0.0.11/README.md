# some_pypi_package

A simple example Python package.

https://www.youtube.com/watch?v=Kz6IlDCyOUY

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
python setup.py sdist bdist_wheel
```

## Test locally
Replace "0.0.1" with your current version

```bash
pip install dist/some_pypi_package-0.0.1-py3-none-any.whl
pip list
```

## Register to PyPi
Open a pypi account here: https://pypi.org/

## Publish your package
twine upload -u <username> -p <password> dist/*

## Test the new package 
### Create a new project

```bash
mkdir new_project
cd new_project

uv init
uv venv
uv pip install some_pypi_package>=0.0.1
uv pip list
```

### Import the new package
```python main.py
from some_pypi_package import hello
hello()
```

```bash
uv run main.py
```
