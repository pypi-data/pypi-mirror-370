# This file is part of Dictdiffer.
#
# Copyright (C) 2013 Fatih Erikli.
# Copyright (C) 2014, 2015, 2016 CERN.
# Copyright (C) 2017, 2019 ETH Zurich, Swiss Data Science Center, Jiri Kuncar.
#
# Dictdiffer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more
# details.

"""Dictdiffer is a library that helps you to diff and patch dictionaries."""

from __future__ import absolute_import, print_function


from setuptools import find_packages, setup

readme = "Dictdiffer is a helper module that helps you to diff and patch dictionaries."

tests_require = [
    'pytest~=4.6; python_version == "2.7"',
    'pytest~=8.0,>=8.3.5; python_version >= "3"',
]

extras_require = {
    "numpy": [
        'numpy>=1.16.0;python_version<"3.7"',
        'numpy>=2.2.6;python_version>="3.11"',
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for key, reqs in extras_require.items():
    if ":" == key[0]:
        continue
    extras_require["all"].extend(reqs)

packages = find_packages()

setup(
    name="inspire-dictdiffer",
    description=__doc__,
    long_description=readme,
    author="Invenio Collaboration",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/dictdiffer",
    packages=["inspire_dictdiffer"],
    zip_safe=False,
    extras_require=extras_require,
    tests_require=tests_require,
    version="0.0.6",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
