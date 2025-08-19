#!/usr/bin/env python3
"""Setup script for Multi-Agent Bot Framework."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
requirements = []
requirements_path = os.path.join(this_directory, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="multi-agent-bot",
    version="1.0.0",
    author="jpalvarezb",
    author_email="jpalvarezb@users.noreply.github.com",
    description="A multi-agent bot framework for research and automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpalvarezb/multi-agent-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
