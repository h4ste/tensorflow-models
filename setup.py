#!/usr/bin/env python

import os

from setuptools import setup, find_packages

setup(name='tensorflow-models',
      version='2.0.0',
      author='Google',
      keywords='tensorflow',
      package_dir={'' : 'official'}
      long_description=os.open(os.path.join(os.path.dirname(__file__), 'official', 'README.md')).read(),
      install_requires=open(os.path.join(os.path.dirname(__file__), 'official', 'requirements.txt')).read(),
      packages=find_packages()
      )
