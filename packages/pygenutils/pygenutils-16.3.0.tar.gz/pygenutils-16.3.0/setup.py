#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt

# Generate creation date
CREATION_DATE = dt.now().strftime("%F %T")

"""
**Note**
This setup.py file is provided for backward compatibility.
The project now uses pyproject.toml for configuration.
This file will be removed in a future version.

Created: {}
""".format(CREATION_DATE)

#----------------#
# Import modules #
#----------------#

from setuptools import setup

# Defer to pyproject.toml for all configuration
setup()
