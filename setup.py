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

$Id: setup.py 110769 2010-04-13 10:30:45Z sidnei $
"""

import os
import sys
if sys.version > '3':
    extras = dict(
    use_2to3 = True,
    convert_2to3_doctests = ['src/zope/testrunner/testrunner-leaks.txt',
                             'src/zope/testrunner/testrunner-leaks-err.txt',
                             'src/zope/testrunner/testrunner-progress.txt',
                             'src/zope/testrunner/testrunner-edge-cases.txt',
                             'src/zope/testrunner/testrunner-test-selection.txt',
                             'src/zope/testrunner/testrunner-simple.txt',
                             'src/zope/testrunner/testrunner-ex/README.txt',
                             'src/zope/testrunner/testrunner-ex/sampletests.txt',
                             'src/zope/testrunner/testrunner-ex/usecompiled/README.txt',
                             'src/zope/testrunner/testrunner-ex/sample3/set_trace5.txt',
                             'src/zope/testrunner/testrunner-ex/sample3/post_mortem6.txt',
                             'src/zope/testrunner/testrunner-ex/sample3/post_mortem5.txt',
                             'src/zope/testrunner/testrunner-ex/sample3/set_trace6.txt',
                             'src/zope/testrunner/testrunner-ex/sample3/post_mortem_failure.txt',
                             'src/zope/testrunner/testrunner-ex/sample2/e.txt',
                             'src/zope/testrunner/testrunner-ex/unicode.txt',
                             'src/zope/testrunner/testrunner-ex/sampletestsl.txt',
                             'src/zope/testrunner/testrunner-coverage.txt',
                             'src/zope/testrunner/testrunner-errors.txt',
                             'src/zope/testrunner/testrunner-profiling.txt',
                             'src/zope/testrunner/testrunner-coverage-win32.txt',
                             'src/zope/testrunner/testrunner-knit.txt',
                             'src/zope/testrunner/testrunner-subunit-leaks.txt',
                             'src/zope/testrunner/testrunner-subunit.txt',
                             'src/zope/testrunner/testrunner-layers-buff.txt',
                             'src/zope/testrunner/testrunner-arguments.txt',
                             'src/zope/testrunner/testrunner-shuffle.txt',
                             'src/zope/testrunner/testrunner-layers-ntd.txt',
                             'src/zope/testrunner/testrunner-subunit-err.txt',
                             'src/zope/testrunner/testrunner-gc.txt',
                             'src/zope/testrunner/testrunner-tb-format.txt',
                             'src/zope/testrunner/testrunner-layers.txt',
                             'src/zope/testrunner/testrunner-wo-source.txt',
                             'src/zope/testrunner/testrunner.txt',
                             'src/zope/testrunner/testrunner-profiling-cprofiler.txt',
                             'src/zope/testrunner/testrunner-verbose.txt',
                             'src/zope/testrunner/testrunner-discovery.txt',
                             'src/zope/testrunner/testrunner-layers-api.txt',
                             'src/zope/testrunner/testrunner-colors.txt',
                             'src/zope/testrunner/testrunner-repeat.txt',
                             'src/zope/testrunner/testrunner-debugging.txt',
                             'src/zope/testrunner/testrunner-debugging-layer-setup.test',
                             ],
    dependency_links = ['.'], # Until zope.interface 3.6, zope.exception 3.6
                              # and zope.testing 4.0 has been released.
    )
else:
    extras = {}
    
from setuptools import setup

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

        # The following seems to cause weird unicode in the output: :(
        ##     'testrunner-errors.txt',

        'testrunner-debugging.txt',
        'testrunner-layers-ntd.txt',
        'testrunner-coverage.txt',
        'testrunner-profiling.txt',
        'testrunner-wo-source.txt',
        'testrunner-repeat.txt',
        'testrunner-gc.txt',
        'testrunner-leaks.txt',
        'testrunner-knit.txt',
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
    version = '4.0.0',
    url='http://pypi.python.org/pypi/zope.testrunner',
    license='ZPL 2.1',
    description='Zope testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    packages=["zope", 
              "zope.testrunner", 
              "zope.testrunner.testrunner-ex",
              "zope.testrunner.testrunner-ex.sample1",
              "zope.testrunner.testrunner-ex.sample2",
              "zope.testrunner.testrunner-ex.sample3",
              ],
    package_dir = {'': 'src'},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        ],
    namespace_packages=['zope',],
    install_requires = ['setuptools',
                        'zope.exceptions',
                        'zope.interface',
                        'zope.testing>=4.0.0dev',],
    entry_points = {
        'console_scripts':
            ['zope-testrunner = zope.testrunner:run',]},
    include_package_data = True,
    zip_safe = False,
    **extras
)
