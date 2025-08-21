from distutils.core import setup
from Cython.Build import cythonize

# pip3 --default-timeout=1000 install -U cython
# sudo apt-get  build-dep  gcc


# python3.6 py_to_so.py build_ext --inplace

files = ['command.py']
for f in files:
    setup(ext_modules=cythonize([f]))

