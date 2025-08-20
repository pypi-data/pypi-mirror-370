from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description=f.read()

setup(
    name='some_pypi_package',
    version='0.0.11', # change before building
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
        'numpy>=1.11.1'
    ],
    entry_points={
        "console_scripts": [
            "some-pypi-package = some_pypi_package:hello",
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)
