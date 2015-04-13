import site
import shutil
import os

src = ['numerrin.so', 'numerrin4.so']
destdir = site.getsitepackages()
if type(destdir) is list:
    destdir = destdir[0]
for f in src:
    shutil.copy(f, os.path.join(destdir, f))
