##############################################################################
#
# Copyright (c) 2004, 2013 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
version = '4.6.0'

import os
import sys
from setuptools import setup
from setuptools.command.test import test


INSTALL_REQUIRES = [
    'setuptools',
    'six',
    'zope.exceptions',
    'zope.interface',
]

TESTS_REQUIRE = [
    'zope.testing',
]

EXTRAS_REQUIRE = {
    'test': TESTS_REQUIRE,
    'subunit': TESTS_REQUIRE + ['python-subunit'],
}


CUSTOM_TEST_TEMPLATE = """\
import sys
sys.path = %r

import os
os.chdir(%r)

# The following unused imports are dark magic that makes the tests pass on
# Python 3.5 on Travis CI.  I do not understand why.
import zope.exceptions.exceptionformatter
import zope.testing

import zope.testrunner
if __name__ == '__main__':
    zope.testrunner.run([
        '--test-path', %r, '-c'
        ])
"""


class custom_test(test):
    # The zope.testrunner tests MUST be run using its own testrunner. This is
    # because its subprocess testing will call the script it was run with. We
    # therefore create a script to run the testrunner, and call that.
    def run(self):
        dist = self.distribution

        if dist.install_requires:
            dist.fetch_build_eggs(dist.install_requires)

        if dist.tests_require:
            dist.fetch_build_eggs(dist.tests_require)

        self.with_project_on_sys_path(self.run_tests)

    def run_tests(self):
        import tempfile
        fd, filename = tempfile.mkstemp(prefix='temprunner', text=True)
        scriptfile = open(filename, 'w')
        script = CUSTOM_TEST_TEMPLATE % (
            sys.path, os.path.abspath(os.curdir), os.path.abspath('src'))
        scriptfile.write(script)
        scriptfile.close()

        import subprocess
        process = subprocess.Popen([sys.executable, filename])
        rc = process.wait()
        try:
            os.unlink(filename)
        except OSError as e:
            # This happens on Windows and I don't understand _why_.
            sys.stderr.write("Failed to clean up temporary script %s:\n%s: %s"
                             % (filename, e.__class__.__name__, e))
            sys.stderr.flush()
        sys.exit(rc)

chapters = '\n'.join([
    open(os.path.join('src', 'zope', 'testrunner', 'tests', name)).read()
    for name in (
        'testrunner.txt',
        'testrunner-simple.txt',
        'testrunner-layers-api.txt',
        'testrunner-layers.txt',
        'testrunner-arguments.txt',
        'testrunner-verbose.txt',
        'testrunner-test-selection.txt',
        'testrunner-progress.txt',
        'testrunner-debugging.txt',
        'testrunner-layers-ntd.txt',
        'testrunner-eggsupport.txt',
        'testrunner-coverage.txt',
        'testrunner-profiling.txt',
        'testrunner-wo-source.txt',
        'testrunner-repeat.txt',
        'testrunner-gc.txt',
        'testrunner-leaks.txt',
        'testrunner-knit.txt',
        'testrunner-edge-cases.txt',
        'testrunner-subunit.txt',

        # The following seems to cause weird unicode in the output: :(
             'testrunner-errors.txt',

    )])

long_description=(
    open('README.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' + chapters
    )

setup(
    name='zope.testrunner',
    version=version,
    url='http://pypi.python.org/pypi/zope.testrunner',
    license='ZPL 2.1',
    description='Zope testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    packages=["zope", "zope.testrunner", "zope.testrunner.tests.testrunner-ex"],
    package_dir = {'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        ],
    namespace_packages=['zope',],
    install_requires = INSTALL_REQUIRES,
    tests_require = TESTS_REQUIRE,
    extras_require = EXTRAS_REQUIRE,
    entry_points = {
        'console_scripts':
            ['zope-testrunner = zope.testrunner:run',],
        'distutils.commands': [
            'ftest = zope.testrunner.eggsupport:ftest',],
        },
    include_package_data = True,
    zip_safe = False,
    cmdclass = {
        'test': custom_test,
    },
)
