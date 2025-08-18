#!/usr/bin/env python
import os
import sys

from setuptools import find_packages, setup

sys.path.insert(0, os.path.dirname(__file__))

try:
    from version import __version__
except ImportError:
    __version__ = "0.0.1"

__author__ = "Akinon"
__license__ = "MIT"
__maintainer__ = "Akinon"
__email__ = "dev@akinon.com"

if sys.version_info[0] == 2:
    from io import open

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="dj-flexi-tag",
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    description="Add tags to any model in Django via ModelViewSet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=__license__,
    url="https://bitbucket.org/akinonteam/dj-flexi-tag",
    project_urls={
        "Documentation": "https://dj-flexi-tag.readthedocs.io",
        "Source Code": "https://bitbucket.org/akinonteam/dj-flexi-tag",
    },
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    platforms="any",
    zip_safe=False,
    use_scm_version={
        "write_to": "./version.py",
        "write_to_template": '__version__ = "{version}"\n',
    },
    install_requires=[
        "Django>=1.10,<5.1",
        "djangorestframework>=3.4.3,<=3.14.0",
        "psycopg2-binary",
        "pytz",
        "typing-extensions",
    ],
    extras_require={
        "dev": [
            "black==21.5b1",
            "isort==5.0.4",
            "tox",
            "click==7.1.2",
        ],
        "test": [
            "mock",
            "importlib-metadata>=1.4.0,<5.0; python_version == '3.7'",
        ],
        "docs": [
            "sphinx-rtd-theme==1.2.0",
            "sphinx==5.3.0",
            "docutils>=0.18",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
)
