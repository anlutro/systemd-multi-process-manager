#!/usr/bin/env python

import os
import setuptools

# allow setup.py to be ran from anywhere
os.chdir(os.path.dirname(os.path.abspath(__file__)))

setuptools.setup(
    name="sdmpm",
    version="0.1",
    license="GPL-3.0",
    description="SystemD multi-process manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Andreas Lutro",
    author_email="anlutro@gmail.com",
    url="https://github.com/anlutro/systemd-multi-process-manager",
    scripts=["src/sdmpm.py"],
)
