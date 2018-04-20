#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('djmoney_rates')


LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='django-money-rates',
    version=version,
    description='Currency conversion for money',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0.2",
    ],
    keywords='django-money-rates',
    author='Federico Frenguelli',
    author_email='synasius@gmail.com',
    url='https://github.com/evonove/django-money-rates',
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    test_suite='runtests',
    install_requires=[
        'Django>=1.9',
        'py-moneyed>=0.6.0,<0.8'
        'six',
    ],
    zip_safe=False,
)
