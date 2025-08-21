# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
# Note: To use the 'upload' functionality of this file, you must:
# $ pipenv install twine --dev
# $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command


"""
windows: C:\\Users\\用户名
mac：用户下面
在用户录下创建.pypirc文件

[distutils]
  index-servers =
    pypi
    PROJECT_NAME

[pypi]
  username = __token__
  password =
"""

# 打包：python setup.py upload
NAME = 'zhousf-lib'
DESCRIPTION = 'a python library of zhousf'
URL = 'https://github.com/MrZhousf/ZhousfLib'
EMAIL = '442553199@qq.com'
AUTHOR = 'zhousf'
REQUIRES_PYTHON = '>=3.6.13'
VERSION = '1.6.8.5.6'
PACKAGE_DATA = {'': ['*.yaml', '*.ttf', '*.txt', '*.md']}
UPLOAD_TO_PYPI = True
PUSH_TO_GITHUB = False


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# What packages are required for this module to be executed?
REQUIRED = [
    # 'requests', 'maya', 'records',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        if UPLOAD_TO_PYPI:
            self.status('Uploading the package to PyPI via Twine…')
            os.system('twine upload dist/* --verbose')

        if PUSH_TO_GITHUB:
            self.status('Pushing git tags…')
            os.system('git tag v{0}'.format(about['__version__']))
            os.system('git push --tags')

        sys.exit()


def read_file(file):
    with open(file, "rt") as f:
        return f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=[i for i in read_file("requirements.txt").strip().splitlines() if i != ''],
    extras_require=EXTRAS,
    package_data=PACKAGE_DATA,
    install_pakcage_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)



