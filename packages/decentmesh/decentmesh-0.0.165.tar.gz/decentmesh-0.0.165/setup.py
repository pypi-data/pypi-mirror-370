#!/usr/decentmesh/env python3

import os

from setuptools import find_packages, setup

# get key package details from decentmesh/__version__.py
about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "decentnet", "__version__.py")) as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open("README.md", "r") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8,<4",
    install_requires=[
        "alembic~=1.13.3",
        "argon2-cffi~=23.1.0",
        "argon2-cffi-bindings~=21.2.0",
        "asn1crypto~=1.5.1",
        "cffi~=1.17.1",
        "coincurve~=20.0.0",
        "pycryptodome~=3.21.0",
        "pynacl~=1.5.0",
        "eth-utils~=5.1.0",
        "lz4~=4.3.3",
        "networkx~=3.4.2",
        "SQLAlchemy~=2.0.36",
        "cbor2~=5.6.5",
        "netifaces~=0.11.0",
        "sentry-sdk~=2.16.0",
    ],
    extras_require={
        "async_db": [
            "greenlet~=3.1.1",
            "aiosqlite~=0.20.0",
        ],
        "dev": [
            "setuptools~=74.1.2",  # Moved here for development purposes
            "black==22.*",
            "numpy~=2.1.2",
        ],
        "metrics": [
            "typing_extensions",
            "hypercorn~=0.17.3",
            "prometheus_client~=0.20.0",
            "httpx~=0.27.2",
            "mdurl~=0.1.2",
            "aiohttp~=3.11.11",
            "Mako~=1.3.5",
            "markdown-it-py~=3.0.0",
            "MarkupSafe~=2.1.5",
        ],
        "cli": [
            "click~=8.1.7",
            "rich~=13.9.2",
            "colorama~=0.4.6",
            "Pygments~=2.18.0",
            "six~=1.16.0",
            "qrcode~=8.0",
        ]
    },
    license=about["__license__"],
    zip_safe=True,
    entry_points={
        "console_scripts": ["decentmesh=decentnet.main:main"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="Decentralized P2P Network",
)
