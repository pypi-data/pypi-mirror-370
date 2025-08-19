# RCSB Python Chemical Search Service

[![Build Status](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_apis/build/status/rcsb.py-rcsb_app_chem?branchName=master)](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_build/latest?definitionId=22&branchName=master)

## Introduction

This module contains application interface to RCSB chemical search services.

### Installation

Download the library source software from the project repository:

```bash

git clone --recurse-submodules https://github.com/rcsb/py-rcsb_app_chem.git

```

Optionally, run test suite (Python 3.8) using
[setuptools](https://setuptools.readthedocs.io/en/latest/) or
[tox](http://tox.readthedocs.io/en/latest/example/platform.html):

```bash
python setup.py test

or simply run

tox
```

Installation is via the program [pip](https://pypi.python.org/pypi/pip).

```bash
pip install rcsb.app.chem

or for the local repository:

pip install .
```
