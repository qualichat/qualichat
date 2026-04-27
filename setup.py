"""Legacy entry point.

All project metadata, dependencies and tool configuration live in
``pyproject.toml`` (PEP 621). This file exists only for older versions of
``pip`` (< 21.3) that do not understand pyproject-only projects.
"""

from setuptools import setup

setup()
