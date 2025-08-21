#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup
setup(
    name='pm_sdk',
    version='0.1.10',
    packages=['pm_sdk'],
    install_requires=[
        'requests>=2.32.1',
    ],
    author='Westboro Photonics',
    description='SDK for interacting with Photometrica',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)