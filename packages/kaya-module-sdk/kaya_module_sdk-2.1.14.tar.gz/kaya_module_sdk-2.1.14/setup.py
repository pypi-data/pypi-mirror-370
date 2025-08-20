#!/usr/bin/env python

import glob
import os
import pkgutil
import subprocess
import sys

import mypy.api
from pylint.lint import Run
from setuptools import Command, setup, find_packages

# [ NOTE ]: Directory where this file is located
root_dir = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = "kaya_module_sdk"
MYPY_CONFIG_FILE = "conf/setup.mypy.conf"
PYLINT_CONFIG_FILE = "conf/setup.pylint.conf"
FLAKE8_CONFIG_FILE = "conf/setup.flake8.conf"
# Update the version here, do not remove the variable. It's used in CI
SDK_VERSION = "2.1.14"


class MyPyCommand(Command):
    """[ NOTE ]: Custom command to run MyPy checks using `python setup.py
    mypy`."""

    description = "Run MyPy type checks"
    user_options: list[str] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        user_options = [
            "--disallow-untyped-defs",
            "--config-file",
            MYPY_CONFIG_FILE,
        ]
        user_options.extend(glob.glob("*.py"))
        result = mypy.api.run(user_options)
        print(f"[ MyPy ]: {result}")

        if result[0]:
            print("[ ERROR ]: MyPy found type errors:")
            print(result[0])
            raise SystemExit(1)

        if result[2]:
            print("[ WARNING ]: MyPy found warnings:")
            print(result[2])


class PyLintCommand(Command):
    """[ NOTE ]: Custom command to run PyLint checks using `python setup.py
    pylint`."""

    description = "Run PyLint type checks"
    user_options: list[str] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        user_options = [
            f"--rcfile={PYLINT_CONFIG_FILE}",
            "--fail-under=8",
            PACKAGE_NAME,
        ]
        Run(user_options)


class Flake8Command(Command):
    description = "Run flake8 checks"
    user_options: list[str] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        user_options = ["flake8", "--config", FLAKE8_CONFIG_FILE, "."]
        subprocess.call(user_options)


def add_package_dir_to_path():
    """[ NOTE ]: Add the package directory to the Python path."""
    package_dir = os.path.join(root_dir, PACKAGE_NAME)
    sys.path.insert(0, package_dir)
    for loader, _, is_pkg in pkgutil.walk_packages([package_dir]):
        # full_name = PACKAGE_NAME + "." + name
        if is_pkg:
            path = loader.path
        else:
            path = os.path.dirname(loader.path)
        sys.path.insert(0, path)


# MISCELLANEOUS

add_package_dir_to_path()
setup_info = dict(
    name="kaya_module_sdk",
    version=SDK_VERSION,
    author="WanoLabs",
    author_email="contact@wanolabs.com",
    url="https://wanolabs.com",
    description="Kaya Module SDK.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    # Package info
    packages=find_packages(exclude=["kaya_module_sdk/tst"]),
    include_package_data=True,
    py_modules=["kaya_module_sdk"],
    zip_safe=True,
    test_suite="KAT",
    cmdclass={
        "flake8": Flake8Command,
        "mypy": MyPyCommand,
        "pylint": PyLintCommand,
    },
    install_requires=["pandas"],
    setup_requires=["flake8", "mypy", "pylint", "setuptools"],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "kaya_module_runner=kaya_module_runner.app:init",
        ]
    },
)

setup(**setup_info)

# CODE DUMP
