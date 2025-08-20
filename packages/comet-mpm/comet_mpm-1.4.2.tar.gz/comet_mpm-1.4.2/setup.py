#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import io
import os
from pathlib import Path

from setuptools import find_packages, setup

requirements = [
    "pandas",
    "typing_extensions>=3.7.4",
    "aiohttp",
    "pydantic",
    "pydantic-settings",
    "requests",
]

# read the contents of your PACKAGE file

HERE = Path(__file__).parent
long_description = (HERE / "README.md").read_text()


def get_version(file, name="__version__"):
    """Get the version of the package from the given file by
    executing it and extracting the given `name`.
    """
    path = os.path.realpath(file)
    version_ns = {}
    with io.open(path, encoding="utf8") as f:
        exec(f.read(), {}, version_ns)
    return version_ns[name]


__version__ = get_version(HERE / "src/comet_mpm/_version.py")

setup(
    name="comet_mpm",
    version=__version__,
    author="Comet ML Inc.",
    author_email="support@comet.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
    ],
    description="Comet MPM SDK",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="comet_mpm",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://www.comet.ml",
    zip_safe=False,
    license="Proprietary",
)
