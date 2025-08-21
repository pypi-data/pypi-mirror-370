#!/usr/bin/env python3
from pathlib import Path
from setuptools import setup, find_namespace_packages

# The directory containing this file
HERE = Path(__file__).parent

# Load version without importing it (see issue #192 if you are confused)
VERSION = [l for l in (HERE / "Cargo.toml").read_text('utf-8').splitlines() if l.startswith("version = ")]
if len(VERSION) != 1:
    raise ValueError(f"Cannot determine version from Cargo.toml: {VERSION}")
VERSION = VERSION[0].split('"')[1]

# The text of the README file
README = (HERE / "README.md").read_text('utf-8')

# This call to setup() does all the work
setup(
    name="HyFetch",
    version=VERSION,
    description="neofetch with flags <3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hykilpikonna/HyFetch",
    author="Azalea Gui",
    author_email="me@hydev.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_namespace_packages(exclude=("tools", "tools.*")),
    package_data={'hyfetch': ['hyfetch/*']},
    include_package_data=True,
    install_requires=[
        # Universal dependencies
        'typing_extensions; python_version < "3.8"',
        
        # Windows dependencies
        'psutil ; platform_system=="Windows"',
        'colorama>=0.4.6 ; platform_system=="Windows"',
    ],
    entry_points={
        "console_scripts": [
            "hyfetch.v1=hyfetch.__main__:run_py",
            "hyfetch.rs=hyfetch.__main__:run_rust",
            "hyfetch=hyfetch.__main__:run_rust",
        ]
    },
    scripts=['hyfetch/scripts/neowofetch']
)
