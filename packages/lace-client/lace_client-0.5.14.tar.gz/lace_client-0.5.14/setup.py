#!/usr/bin/env python3
"""
Setup script for AEGIS client package.
This enables development installation and console script entry points.
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "AEGIS - Cryptographic attestation for AI training data"

setup(
    name="lace-client",
    version="0.5.14",
    author="Aegis Testing Technologies LLC",
    author_email="support@aegisprove.com",
    description="Privacy-preserving copyright proof for AI training data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aegis-Testing-Technologies/aegis-techspike",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "requests>=2.28.0",
        "bitarray>=2.8.0",
        "click>=8.0.0",
        "tqdm>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "aegis=aegis_cli.__main__:main",
            "aegis-cli=aegis_cli.__main__:main",  # Backward compatibility
        ],
    },
    include_package_data=True,
)
