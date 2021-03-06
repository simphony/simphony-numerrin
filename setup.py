import os

from setuptools import setup, find_packages

with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()

VERSION = '0.1.5.dev0'


def write_version_py(filename=None):
    if filename is None:
        filename = os.path.join(
            os.path.dirname(__file__), 'numerrin_wrapper', 'version.py')
    ver = """\
version = '%s'
"""
    fh = open(filename, 'wb')
    try:
        fh.write(ver % VERSION)
    finally:
        fh.close()


write_version_py()

setup(
    name='numerrin_wrapper',
    version=VERSION,
    author='SimPhoNy FP7 European Project',
    description='Implementation of the SimPhoNy Numerrin -wrapper',
    long_description=README_TEXT,
    packages=find_packages(),
    install_requires=['simphony>=0.6'],
    entry_points={
        'simphony.engine': ['numerrin = numerrin_wrapper']}
)
