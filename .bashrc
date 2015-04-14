#!/bin/bash

export LD_LIBRARY_PATH=$(python -c "import sys; print [f for f in sys.path if f.endswith('site-packages')][0]"):$LD_LIBARARY_PATH
