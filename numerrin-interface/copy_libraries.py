import sys
import shutil
import os

src = ['numerrin.so', 'libnumerrin4.so']
destdir = [f for f in sys.path if f.endswith('site-packages')]
if type(destdir) is list:
    destdir = destdir[0]
for f in src:
    shutil.copy(f, os.path.join(destdir, f))
