# botocross

A Python package for operating cross region Amazon Web Services (AWS) resources.

## Status
[![Build Status](https://secure.travis-ci.org/sopel/botocross.png?branch=master)](http://travis-ci.org/sopel/botocross) <br />
[![Build Status](http://ci.labs.cityindex.com:8080/job/botocross/badge/icon)](http://ci.labs.cityindex.com:8080/job/botocross/) <- includes metrics

## Introduction

Botocross is a Python package extending the excellent [boto](https://github.com/boto/boto) with functionality for operating cross region AWS resources - currently it is comprised of:
* a module structured similar to boto, adding cross region functionality on top of boto's API (very early stages, most of this is still provided inline in the scripts and needs to be 
refactored into the respective sub modules still)
* a set of Python scripts for orchestrating cross region AWS resources, i.e. a partial replacement for some AWS command line tools, specifically adding cross region functionality

### Origin

The functionality originated in the [Amazon EC2 clock accuracy research](https://github.com/cityindex/ec2-clock-accuracy-research) project and has been extracted due to being of 
general use in various contexts.

### Status

The package is actively used in the [Amazon EC2 clock accuracy research](https://github.com/cityindex/ec2-clock-accuracy-research) as well as a few other internal projects, 
but still in it's early stages and mainly demand driven - therefore the AWS API coverage is incomplete and likely also inconsistent here and there.

## Requirements

The scripts are based on [Python 2.7](http://python.org/) and have the following dependencies (handled automatically if installed via pip, see below):

* A recent version of [boto](https://github.com/boto/boto) (tested against 2.6.0), which provides the interface to Amazon Web Services

## Installation

Install via [pip](http://www.pip-installer.org/) from PyPI:

**NOTE**: botocross is not yet published to PyPI, please use _Install from GitHub_ or _Install from source_ below).

```sh
$ pip install botocross
```

Install via [pip](http://www.pip-installer.org/) from GitHub:

```sh
$ pip install git+https://github.com/sopel/botocross.git
```

Install from source:

```sh
$ git clone git://github.com/sopel/botocross.git
$ cd botocross
$ python setup.py install
```

## Usage

The scripts provide common command line argument parsing and help functionality (invoke with no arguments, `--help` or `-h`).

AWS credentials are obviously required, which can provided via the command line as well, 
but are more easily served via environment variables or a configuration file for day to day usage, 
see section [Getting Started with Boto](https://github.com/boto/boto#getting-started-with-boto) for details.

* The `validate-credentials` script provides a convenience method to both validate the AWS credentials and 
display respective account/user information, which helps when juggling multiple AWS accounts.

# License
 
Licensed under the MIT License (MIT), see LICENSE for details.
