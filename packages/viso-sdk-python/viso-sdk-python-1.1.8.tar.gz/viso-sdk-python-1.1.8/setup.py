#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from Cython.Build import cythonize
from setuptools_cythonize import get_cmdclass

from codecs import open
from os import path

# from viso_sdk import __version__

here = path.abspath(path.dirname(__file__))


def read_version():
    with open(path.join(here, "viso_sdk", "_version.py"), "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.strip().split()[-1][1:-1]
    raise RuntimeError("Unable to find version string.")


__version__ = read_version()

with open(path.join(here, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="viso-sdk-python",
    cmdclass=get_cmdclass(),
    version=__version__,
    description="VisoSDK: A Python SDK for use in Viso containers",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="support@viso.ai",
    author_email="support@viso.ai",
    # choose license
    license="LGPLv3",
    url="https://gitlab.com/TopKamera/03_edge/Base/viso-sdk-python-public.git",
    packages=find_packages(exclude=["docs", "tests", "contrib"]),
    include_package_data=True,
    install_requires=[
        "requests",
        "requests-toolbelt",
        "setuptools",
        "paho-mqtt",
        "redis",
        "opencv-contrib-python-headless~=4.10.0",
        "Pillow",
        "cython~=3.0.2",
        "numpy~=1.26.2",
        "six~=1.16.0",
        "traceback2~=1.4.0",
        "shapely~=2.0.7"
    ],
    package_data={"viso_sdk": ["assets/*", "assets/*/*"]},
    python_requires=">=3.6.0",
    entry_points={},
    # dependency_links=["https://www.piwheels.org/simple"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    ext_modules=cythonize("viso_sdk/**/*.py", compiler_directives={"language_level": "3"}),
    # options={"bdist_wheel": {"universal": True}},
    # extras_require={
    #     "autocompletion": ["argcomplete>=1.10.0,<3"],
    #     "yaml": ["PyYaml>=5.2"],
    # },
)
