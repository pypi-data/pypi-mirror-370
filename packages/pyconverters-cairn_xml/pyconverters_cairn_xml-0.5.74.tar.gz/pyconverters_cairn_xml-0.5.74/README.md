# pyconverters_cairn_xml

[![license](https://img.shields.io/github/license/oterrier/pyconverters_cairn_xml)](https://github.com/oterrier/pyconverters_cairn_xml/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyconverters_cairn_xml/workflows/tests/badge.svg)](https://github.com/oterrier/pyconverters_cairn_xml/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyconverters_cairn_xml)](https://codecov.io/gh/oterrier/pyconverters_cairn_xml)
[![docs](https://img.shields.io/readthedocs/pyconverters_cairn_xml)](https://pyconverters_cairn_xml.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyconverters_cairn_xml)](https://pypi.org/project/pyconverters_cairn_xml/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyconverters_cairn_xml)](https://pypi.org/project/pyconverters_cairn_xml/)

Fetch articles from Pubmed

## Installation

You can simply `pip install pyconverters_cairn_xml`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyconverters_cairn_xml
```

### Running the test suite

You can run the full test suite against all supported versions of Python (3.8) with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
