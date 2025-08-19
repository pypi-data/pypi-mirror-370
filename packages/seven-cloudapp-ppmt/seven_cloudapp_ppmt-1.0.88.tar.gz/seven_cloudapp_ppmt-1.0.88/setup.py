# -*- coding: utf-8 -*-
"""
@Author: HuangJingCan
@Date: 2020-08-21 14:59:50
@LastEditTime: 2020-08-21 14:59:50
@LastEditors: HuangJingCan
@Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_cloudapp_ppmt",
    version="1.0.88",
    author="seven",
    author_email="tech@gao7.com",
    description="seven cloudapp ppmt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/TaoBaoCloud/seven_cloudapp_ppmt.git",
    packages=find_packages(),
    install_requires=[
        "seven-cloudapp>=1.0.210",
        "bce-python-sdk==0.8.61"
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='~=3.4',
)
