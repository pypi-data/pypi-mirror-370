# pyprocessors_opennre

[![license](https://img.shields.io/github/license/oterrier/pyprocessors_opennre)](https://github.com/oterrier/pyprocessors_opennre/blob/master/LICENSE)
[![tests](https://github.com/oterrier/pyprocessors_opennre/workflows/tests/badge.svg)](https://github.com/oterrier/pyprocessors_opennre/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/oterrier/pyprocessors_opennre)](https://codecov.io/gh/oterrier/pyprocessors_opennre)
[![docs](https://img.shields.io/readthedocs/pyprocessors_opennre)](https://pyprocessors_opennre.readthedocs.io)
[![version](https://img.shields.io/pypi/v/pyprocessors_opennre)](https://pypi.org/project/pyprocessors_opennre/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyprocessors_opennre)](https://pypi.org/project/pyprocessors_opennre/)

Processor based on Facebook's OpenNRE

## Installation

You can simply `pip install pyprocessors_opennre`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/oterrier/pyprocessors_opennre
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
