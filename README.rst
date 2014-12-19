simphony-numerrin
===============

The implementation of the SimPhoNy Numerrin -wrapper.

.. image:: https://travis-ci.org/simphony/simphony-numerrin.svg?branch=master
    :target: https://travis-ci.org/simphony/simphony-numerrin

Repository
----------

Simphony-openfoam is hosted on github: https://github.com/simphony/simphony-numerrin

Installation
------------

The package requires python 2.7.x, installation is based on setuptools::

    # build and install
    python setup.py install

or::

    # build for in-place development
    python setup.py develop

License for Numerrin
--------------------

If you wish to test the Numerrin-related stuff, you need a license file. For this, please send the MAC address of the ethernet adapter of your computer to Janne at Numerola. After getting the file, make an environment variable PYNUMERRIN_LICENSE, which points to the file, for example "/home/user/simphony/license.dat" or "C:\users\meself\license.dat".

Testing
-------

To run the full test-suite run::

    python -m unittest discover


Directory structure
-------------------

Subpackages:

- numerrin_wrapper --  wrapper class and tests for Numerrin -wrapper 

