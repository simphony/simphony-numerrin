#!/bin/bash
set -e

pushd numerrin-interface
python copy_libraries.py
popd
