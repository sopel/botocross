#!/usr/bin/python
from distutils.core import setup
from setuptools import find_packages
import sys

if sys.version_info <= (2, 4):
    error = "ERROR: botocross requires Python Version 2.5 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

setup(name="botocross",
      version="1.0.9",
      author = "Steffen Opel",
      packages=find_packages(),
      scripts=[
        'scripts/authorize-securitygroups.py',
        'scripts/create-buckets.py',
        'scripts/create-images.py',
        'scripts/create-securitygroups.py',
        'scripts/create-snapshots.py',
        'scripts/create-stacks.py',
        'scripts/create-topics.py',
        'scripts/decode-logs.py',
        'scripts/delete-buckets.py',
        'scripts/delete-images.py',
        'scripts/delete-keypairs.py',
        'scripts/delete-keys.py',
        'scripts/delete-securitygroups.py',
        'scripts/delete-snapshots.py',
        'scripts/delete-stacks.py',
        'scripts/delete-topics.py',
        'scripts/describe-images.py',
        'scripts/describe-instances.py',
        'scripts/describe-regions.py',
        'scripts/describe-securitygroups.py',
        'scripts/describe-snapshots.py',
        'scripts/describe-stacks.py',
        'scripts/describe-tags.py',
        'scripts/describe-volumes.py',
        'scripts/import-keypairs.py',
        'scripts/read-buckets.py',
        'scripts/revoke-securitygroups.py',
        'scripts/subscribe-topics.py',
        'scripts/update-stacks.py',
        'scripts/upload-keys.py',
        'scripts/validate-credentials.py',
        'scripts/validate-template.py',
      ],
      license="MIT",
      platforms = "Posix; MacOS X; Windows",
      install_requires=[
        "boto >= 2.6.0",
      ],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet",
          ],
      )
