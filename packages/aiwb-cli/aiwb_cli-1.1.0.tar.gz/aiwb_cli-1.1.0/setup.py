import codecs
import os.path
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

DEPENDENCIES = ["requests", "click~=8.1.7", "python-dateutil", "rich==14.0.0"]

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: Apache Software License",
]


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.rst", encoding="utf-8") as f:
    README = f.read()

setup_options = dict(
    name="aiwb-cli",
    version=find_version("aiwb", "__init__.py"),
    description="Renesas AI Workbench Command-Line Tools.",
    long_description=README,
    author="Renesas AI Workbench",
    url="https://ai.aws.renesasworkbench.com/",
    scripts=["bin/aiwb", "bin/aiwb.cmd"],
    packages=find_packages(exclude=["tests*"]),
    install_requires=DEPENDENCIES,
    license="Apache License 2.0",
    python_requires=">= 3.10",
    classifiers=CLASSIFIERS,
)

setup(**setup_options)
