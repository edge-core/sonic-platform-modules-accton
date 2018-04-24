#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='wedge100bf_32x',
   version='1.0',
   description='Module to initialize Accton WEDGE100BF-32X platforms',
   
   packages=['wedge100bf_32x'],
   package_dir={'wedge100bf_32x': 'wedge100bf-32x/classes'},
)

