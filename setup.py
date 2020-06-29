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
import os
import sys
from setuptools import setup
from setuptools.command.test import test

version = '5.2'

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
    'subunit': [
        'python-subunit >= 0.0.11',
        'testtools >= 0.9.30',
    ],
    'docs': [
        'Sphinx',
        'sphinxcontrib-programoutput',
    ],
}


CUSTOM_TEST_TEMPLATE = """\
import sys
sys.path = %r

try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()

import os
os.chdir(%r)

# The following unused imports are dark magic that makes the tests pass on
# Python 3.5 on Travis CI.  I do not understand why.
import zope.exceptions.exceptionformatter
import zope.testing

import zope.testrunner
if __name__ == '__main__':
    zope.testrunner.run([
        '--test-path', %r, '-c',
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
        script = CUSTOM_TEST_TEMPLATE % (
            sys.path, os.path.abspath(os.curdir), os.path.abspath('src'))
        _fd, filename = tempfile.mkstemp(prefix='temprunner', text=True)
        with open(filename, 'w') as scriptfile:
            scriptfile.write(script)

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


def read(*names):
    with open(os.path.join(*names)) as f:
        return f.read()


long_description = (
    read('README.rst')
    + '\n\n' +
    read("docs", 'getting-started.rst')
    + '\n\n' +
    read('CHANGES.rst')
)

setup(
    name='zope.testrunner',
    version=version,
    url='https://github.com/zopefoundation/zope.testrunner',
    license='ZPL 2.1',
    description='Zope testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    packages=[
        "zope",
        "zope.testrunner",
        "zope.testrunner.tests.testrunner-ex",
    ],
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    namespace_packages=['zope'],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
    entry_points={
        'console_scripts':
            ['zope-testrunner = zope.testrunner:run'],
        'distutils.commands': [
            'ftest = zope.testrunner.eggsupport:ftest'],
    },
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'test': custom_test,
    },
)
