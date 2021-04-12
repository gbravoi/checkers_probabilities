#!/usr/bin/env python
"""
This file is needed to make visible the python packages by the other ROS packages
more info: https://docs.python.org/3/distutils/examples.html
"""
from catkin_pkg.python_setup import generate_distutils_setup
from distutils.core import setup

d = generate_distutils_setup(
    packages=['montecarlo','checkers'],
    package_dir={'': ''}
)

setup(**d)




