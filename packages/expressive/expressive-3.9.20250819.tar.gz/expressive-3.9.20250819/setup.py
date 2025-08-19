#!/usr/bin/env python3

""" Copyright 2024-2025 Russell Fordyce

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import sys
from setuptools import setup

# get version
version = None
path_version = "src/expressive/version.py"
RE_version = r'^version = "(\d+\.\d+\.\d+)"'
with open(path_version) as fh:
    for line in fh:
        match = re.match(RE_version, line)
        if match:
            version = match.group(1)
            break
if not version:
    sys.exit(f"failed to parse version from {path_version}, must match '{RE_version}'")


setup(
    name="expressive",
    version=version,
    description="A library for quickly applying symbolic expressions to NumPy arrays",
    url="https://gitlab.com/expressive-py/expressive",
    maintainer="Russell Fordyce",
    license="Apache License 2.0",
    license_files=["LICENSE.txt"],
    keywords="sympy numba numpy codegen",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
    ],
    packages=["expressive"],
    package_dir={"": "src"},
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    python_requires=">=3.7",
    install_requires=[
        "sympy >= 1.6",
        "numpy >= 1.21.6",
        "numba >= 0.53.0",
        # "llvmlite",  # let Numba figure out its own llvmlite dep
    ],
    #include_package_data=True,
    zip_safe=False,  # https://setuptools.pypa.io/en/latest/deprecated/zip_safe.html
)
