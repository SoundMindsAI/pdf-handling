#!/usr/bin/env python3
"""
Setup script for the pdf_processor package.
"""

from setuptools import setup, find_packages
import os

# Read version from the package
about = {}
with open(os.path.join('pdf_processor', '__init__.py'), 'r') as f:
    exec(f.read(), about)

# Read requirements from requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip()]

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="pdf_processor",
    version=about['__version__'],
    author=about['__author__'],
    author_email="info@example.com",
    description="A toolkit for extracting and processing PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/pdf-processor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pdf-processor=pdf_processor.__main__:main',
        ],
    },
    include_package_data=True,
)
