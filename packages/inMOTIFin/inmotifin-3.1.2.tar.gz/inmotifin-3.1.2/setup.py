#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

# dependencies (only pip packages) to automatically install

from pathlib import Path
this_directory = Path(__file__).parent

requirements = [
    'click',
    'numpy',
    'pandas',
    'dagsim',
    'pyjaspar==3.0.0',
    'biopython']

setup(
    author="Katalin Ferenc",
    author_email='katalitf@uio.no',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    description="inMOTIFin",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='inMOTIFin',
    name='inMOTIFin',
    packages=find_packages(include=['inmotifin', "inmotifin.*"]),
    test_suite='tests',
    url='https://bitbucket.org/CBGR/inmotifin/src/main/',
    version='3.1.2',
    zip_safe=False,
)
