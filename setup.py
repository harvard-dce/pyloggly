import os
import re
import sys
import codecs
from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

here = os.path.abspath(os.path.dirname(__file__))

def read(path):
    return codecs.open(os.path.join(here, path), 'r', 'utf-8').read()

version_file = read('pyloggly/__init__.py')
version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M).group(1)

setup(
    name='pyloggly',
    version=version,
    packages=find_packages(),
    url='https://github.com/harvard-dce/pyloggly',
    license='MIT License',
    author='Jay Luker',
    author_email='lbjay@reallywow.com',
    description='Python logging handler for loggly',
    install_requires=['requests-futures', 'python-json-logger'],
    tests_require=['pytest', 'mock'],
    cmdclass={'test': PyTest},
    keywords='loggly logging',
    zip_safe=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    )
)
