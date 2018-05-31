#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='common',
   version='1.1',
   description='Module to initialize Accton platforms common module',
   
   packages=['common'],
   package_dir={'common': 'common/classes'},
)

