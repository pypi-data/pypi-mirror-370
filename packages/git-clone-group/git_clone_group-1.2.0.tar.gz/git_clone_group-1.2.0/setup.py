#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from pathlib import Path
from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "git-clone-group"
DESCRIPTION = "Clone all GitLab group projects (Protected Version)"
URL = "https://github.com/bpzhang/git_clone_group"
EMAIL = "zbp1024@gmail.com"
AUTHOR = "bp zhang"
REQUIRES_PYTHON = ">=3.7.0"

REQUIRED = [
    "requests>=2.28.0",
    "tqdm>=4.65.0",
    "aiohttp>=3.8.0",
    "pyarmor>=8.0.0",
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "..", "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load version
about = {}
with open(os.path.join(here, "git_clone_group", "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_data={
        "git_clone_group": ["*.so", "*.pyd", "*.key", "*.lic", "pyarmor_runtime_*"],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "git-clone-group=git_clone_group.cli:cli",
            "gcg=git_clone_group.cli:cli",
        ],
    },
    license="Commercial",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
