#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import setuptools

base = os.path.dirname(sys.argv[0])

version_file = os.path.join(base, "sciexp2", "expdef", "__init__.py")
with open(version_file, encoding="utf-8") as f:
    code = compile(f.read(), version_file, 'exec')
    version = {}
    exec(code, {}, version) #, global_vars, local_vars)

with open(os.path.join(base, "README.md")) as f:
    readme = f.read()
long_description = re.match(r"[\w-]+\n=+\n(.*)\nCopyright$\n=========$", readme,
                            re.MULTILINE | re.DOTALL).group(1)
long_description = long_description.strip()

with open(os.path.join(base, ".requirements.txt"), "r") as f:
    reqs = [line[:-1] for line in f.readlines()]

setuptools.setup(
    name="sciexp2-expdef",
    version=version["__version__"],
    description="Experiment definition framework for SciExp²",
    long_description=long_description,
    author="Lluís Vilanova",
    author_email="llvilanovag@gmail.com",
    url="https://sciexp2-expdef.readthedocs.io/",
    license="GNU General Public License (GPL) version 3 or later",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    packages=["sciexp2", "sciexp2.common", "sciexp2.expdef", "sciexp2.expdef.system"],
    package_data={"sciexp2.expdef": ["templates/*.dsc", "templates/*.tpl"]},
    scripts=["launcher"],
    install_requires=reqs,
    platforms="any",
)
