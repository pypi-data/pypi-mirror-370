#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" setup.py for pypi """

import os
from setuptools import setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "ix_notifiers", "constants.py"), "r", encoding="utf-8") as f:
    # pylint: disable-next=exec-used
    exec(f.read(), about)

# Both VERSION and BUILD are set by build.sh in the pipeline
version = about['VERSION']

if about['BUILD']:
    version += f'.{about['BUILD']}'

setup(version=version)
