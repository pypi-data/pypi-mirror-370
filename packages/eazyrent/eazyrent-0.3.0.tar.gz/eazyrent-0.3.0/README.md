# Overview

Software development kit for Eazyrent

[![PyPI License](https://img.shields.io/pypi/l/eazyrent_sdk.svg)](https://pypi.org/project/eazyrent_sdk)
[![PyPI Version](https://img.shields.io/pypi/v/eazyrent_sdk.svg?label=version)](https://pypi.org/project/eazyrent_sdk)
[![PyPI Downloads](https://img.shields.io/pypi/dm/eazyrent_sdk.svg?color=orange)](https://pypistats.org/packages/eazyrent_sdk)

## Setup

### Requirements

* Python 3.10+

### Installation

Install it directly into an activated virtual environment:

```text
$ pip install eazyrent
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add eazyrent
```

## Usage

After installation, the package can be imported:

```text
$ python
>>> import eazyrent
>>> eazyrent.__version__
```


## API clients

* Core
    - v1 
    - v2 [**documentation**](eazyrent/core/v2_README.md)
* Products
    - v1 [**documentation**](eazyrent/products/v1_README.md)
* IAM
    - v1 [**documentation**](eazyrent/iam/v1_README.md)