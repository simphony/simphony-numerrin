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

After installation ensure that:
  - "libnumerrin4.so" is in the library search path (e.g. in LD_LIBRARY_PATH on linux)
  - "numerrin.so" is in the pythons module search path. This can be accomplished by copying the "numerrin.so" file to under site-packages directory. In standard linux python installation this directory is "/usr/local/lib/python2.7/site-packages/"

Library files "libnumerrin4.so" and "numerrin.so" are found under "numerrin-interface" -directory.


License for Numerrin
--------------------

If you wish to test the Numerrin-related stuff, you need a license file. For this, please send the MAC address of the ethernet adapter of your computer to Janne at Numerola. After getting the file, make an environment variable PYNUMERRIN_LICENSE, which points to the file, for example "/home/user/simphony/license.dat" or "C:\\users\\meself\\license.dat".

Testing
-------

To run the full test-suite run::

    python -m unittest discover


Directory structure
-------------------

Subpackages:

- numerrin_wrapper --  wrapper class and tests for Numerrin -wrapper 

