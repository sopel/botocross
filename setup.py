#!/usr/bin/python
from distutils.core import setup
from setuptools import find_packages

setup(name='botocross',
      version='1.0',
      packages=find_packages(),
      install_requires=[
        "boto >= 2.5.2",
      ],
      )
