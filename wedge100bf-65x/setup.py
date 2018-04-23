#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='wedge100bf_65x',
   version='1.0',
   description='Module to initialize Accton WEDGE100BF-65X platforms',
   
   packages=['wedge100bf_65x'],
   package_dir={'wedge100bf_65x': 'wedge100bf-65x/classes'},
)

