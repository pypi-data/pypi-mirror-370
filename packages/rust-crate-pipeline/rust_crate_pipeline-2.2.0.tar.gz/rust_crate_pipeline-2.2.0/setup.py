#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for rust-crate-pipeline package.
"""

import re
from setuptools import setup, find_packages


def get_version():
    """Extract version from version.py without importing."""
    version_file = "rust_crate_pipeline/version.py"
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise ValueError("Could not find version in version.py")


# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rust-crate-pipeline",
    version=get_version(),
    author="SigilDERG Team",
    author_email="sigilderg@example.com",
    description=(
        "A comprehensive pipeline for analyzing Rust crates with AI enrichment " "and enhanced scraping"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SigilDERG/rust-crate-pipeline",
    packages=find_packages() + ["utils"],  # Include utils module
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "rust-crate-pipeline=rust_crate_pipeline.main:main",
            "sigil-pipeline=rust_crate_pipeline.unified_pipeline:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
