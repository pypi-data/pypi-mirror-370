#!/usr/bin/env python

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(name='boxai',
      version='0.0.0',
      description='Librarie for sandbox ai',
      maintainer='mourad mourafiq',
      maintainer_email='mourad.mourafiq@gmail.com',
      author='mourad mourafiq',
      author_email='mourad.mourafiq@gmail.com',
      url='https://github.com/mmourafiq/sandboxai',
      license='Apache 2.0',
      platforms='any',
      packages=find_packages(),
      cmdclass={'test': PyTest})
