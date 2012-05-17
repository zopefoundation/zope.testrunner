##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Setup for zope.testrunner package
"""

import os
import sys
from setuptools import setup
from setuptools.command.test import test

if sys.version_info < (2,4) or sys.version_info[:2] == (3,0):
    raise ValueError("zope.testrunner requires Python 2.4 or higher, "
                     "or 3.1 or higher.")



if sys.version_info >= (3,):
    extra = dict(use_2to3 = True,
                 setup_requires = ['zope.fixers'],
                 use_2to3_fixers = ['zope.fixers'],
                 convert_2to3_doctests = [
                     'src/zope/testrunner/testrunner-arguments.txt',
                     'src/zope/testrunner/testrunner-coverage-win32.txt',
                     'src/zope/testrunner/testrunner-coverage.txt',
                     'src/zope/testrunner/testrunner-debugging-layer-setup.test',
                     'src/zope/testrunner/testrunner-debugging.txt',
                     'src/zope/testrunner/testrunner-discovery',
                     'src/zope/testrunner/testrunner-edge-cases.txt',
                     'src/zope/testrunner/testrunner-errors.txt',
                     'src/zope/testrunner/testrunner-gc.txt',
                     'src/zope/testrunner/testrunner-knit.txt',
                     'src/zope/testrunner/testrunner-layers-api.txt',
                     'src/zope/testrunner/testrunner-layers-buff.txt',
                     'src/zope/testrunner/testrunner-layers-ntd.txt',
                     'src/zope/testrunner/testrunner-layers.txt',
                     'src/zope/testrunner/testrunner-leaks-err.txt',
                     'src/zope/testrunner/testrunner-leaks.txt',
                     'src/zope/testrunner/testrunner-profiling-cprofiler.txt',
                     'src/zope/testrunner/testrunner-profiling.txt',
                     'src/zope/testrunner/testrunner-progress.txt',
                     'src/zope/testrunner/testrunner-repeat.txt',
                     'src/zope/testrunner/testrunner-simple.txt',
                     'src/zope/testrunner/testrunner-tb-format.txt',
                     'src/zope/testrunner/testrunner-test-selection.txt',
                     'src/zope/testrunner/testrunner-verbose.txt',
                     'src/zope/testrunner/testrunner-wo-source.txt',
                     'src/zope/testrunner/testrunner.txt',
                     'src/zope/testrunner/testrunner-ex/sampletests.txt',
                     'src/zope/testrunner/testrunner-ex/sampletestsl.txt',
                     'src/zope/testrunner/testrunner-ex/unicode.txt',
                     ],
                 # Needed until Python 3 versions of all dependencies are
                 # released on PyPI:
                 dependency_links = ['.'],

                 # XXX:  python-subunit is not yet ported to Python3.
                 tests_require = ['zope.testing'],
                 extras_require = {'test': ['zope.testing']},
                 )
else:
    extra = dict(tests_require = ['zope.testing',
                                  'python-subunit',
                                 ],
                 extras_require = {'test': ['zope.testing',
                                            'python-subunit',
                                           ]},
                )



class custom_test(test):
    # The zope.testrunner tests MUST be run using it's own testrunner. This is
    # because it's subprocess testing will call the script it was run with. We
    # therefore create a script to run the testrunner, and call that.
    def run(self):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)
        self.with_project_on_sys_path(self.run_tests)

    def run_tests(self):
        template = """
import sys
sys.path = %s

import os
os.chdir('%s')

import zope.testrunner
if __name__ == '__main__':
    zope.testrunner.run([
        '--test-path', '%s', '-c'
        ])
        """
        import tempfile
        fd, filename = tempfile.mkstemp(prefix='temprunner', text=True)
        scriptfile = open(filename, 'w')
        script = template % (sys.path, os.path.abspath(os.curdir), os.path.abspath('src'))
        scriptfile.write(script)
        scriptfile.close()

        import subprocess
        process = subprocess.Popen([sys.executable, filename])
        process.wait()
        os.unlink(filename)

chapters = '\n'.join([
    open(os.path.join('src', 'zope', 'testrunner', name)).read()
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
        'testrunner-coverage.txt',
        'testrunner-profiling.txt',
        'testrunner-wo-source.txt',
        'testrunner-repeat.txt',
        'testrunner-gc.txt',
        'testrunner-leaks.txt',
        'testrunner-knit.txt',
        'testrunner-edge-cases.txt',

        # The following seems to cause weird unicode in the output: :(
             'testrunner-errors.txt',

    )])

long_description=(
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' + chapters
    )

setup(
    name='zope.testrunner',
    version='4.1.0dev',
    url='http://pypi.python.org/pypi/zope.testrunner',
    license='ZPL 2.1',
    description='Zope testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    packages=["zope", "zope.testrunner", "zope.testrunner.testrunner-ex"],
    package_dir = {'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        ],
    namespace_packages=['zope',],
    install_requires = ['setuptools',
                        'zope.exceptions',
                        'zope.interface',
                       ],
    entry_points = {
        'console_scripts':
            ['zope-testrunner = zope.testrunner:run',]},
    include_package_data = True,
    zip_safe = False,
    cmdclass = {'test': custom_test},
    **extra
)
