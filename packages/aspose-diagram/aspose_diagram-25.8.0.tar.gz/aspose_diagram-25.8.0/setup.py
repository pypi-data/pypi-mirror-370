# coding: utf-8

import sys
from setuptools import setup, find_packages

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

NAME = "aspose_diagram"
VERSION = "25.8.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["JPype1 >= 1.2.1"]

setup(
    name=NAME,
    version=VERSION,
    description="A powerful library for working with Microsoft Visio files VDX, VSD,VSDX,VSSX,VSTX, VTX, XPS, HTML, SVG",
    author="Aspose",
    author_email="diagram@aspose.com",
    url="https://products.aspose.com/diagram/python-java",
    keywords=["Visio", "VSD", "VDX", "VSDX", "VDW", "to", "PDF", "JPG", "PNG", "HTML", "SVG", "XPS","VSTX", "VSSX"],
    install_requires=REQUIRES,
    packages=['asposediagram'],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'License :: Other/Proprietary License'
    ],
    platforms=[
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.5',
)
