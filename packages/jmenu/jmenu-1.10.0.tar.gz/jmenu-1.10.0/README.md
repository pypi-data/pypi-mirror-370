# jmenu

Command line tool for fetching University of Oulu restaurant menus from the [Jamix API.](https://fi.jamix.cloud/apps/menuservice/rest)

Doubles as a general library for fetching menu info from Jamix.

## Installing

### Python Package Index

jmenu is available for install on the [python package index.](https://pypi.org/project/jmenu/)

```shell
pip install jmenu
```

### Building from source

For testing purposes, the package can be built from the repository source code.

```shell
pip install build
python3 -m build
pip install dist/<package_name>.whl
```

## Usage

### Command line tool

jmenu can be invoked from the command line as is:

```shell
jmenu [-h] [-v] [-e] [-t] [-l {fi,en}] [-a markers [G, VEG ...]]
```

All flags and parameters described below

| Argument        | Example | Description                             |
| :-------------- | :------ | :-------------------------------------- |
| -a, --allergens | g veg   | Highlights appropriately marked results |

| Flag           | Description                         |
| :------------- | :---------------------------------- |
| -h, --help     | Display usage information           |
| -v, --version  | Display version information         |
| -e, --explain  | Display allergen marker information |
| -t, --tomorrow | Fetch menu results for tomorrow     |
| -l, --language | Result language, opts: {fi, en}     |

### Python library

jmenu can also be imported as a library:

```python
from jmenu import main

main.run()
```

Documentation for the library can be found in the [project pages.](https://jkerola.github.io/jmenu)

## Contributing

Pull requests are welcome. We use [pre-commit hooks](https://pre-commit.com/) and GitHub actions to ensure code quality.

### Development environment setup

**Requirements**

- Python 3.10+
- Virtualenv

Setup the development environment with

```shell
python3 -m virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

### Testing

Run the tool

```shell
python3 -m src.jmenu.main
```

Execute unit tests

```shell
pytest
```

# Documentation

Documentation for the project is available in the [project pages.](https://jkerola.github.io/jmenu)

## Build documentation from source

The documentation for the modules is built with [Mkdocs.](https://mkdocs.org) and the mkdocstrings extension, using google style docstrings.

You can build it from source by installing mkdocs

```shell
pip install mkdocs mkdocs-material
mkdocs serve
```

and navigating to [localhost:8000](http://localhost:8000) in your browser.
