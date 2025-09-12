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

from setuptools import setup


version = '8.0'

INSTALL_REQUIRES = [
    'setuptools',
    'zope.exceptions',
    'zope.interface',
]

TESTS_REQUIRE = [
    'zope.testing',
]

EXTRAS_REQUIRE = {
    'test': TESTS_REQUIRE,
    'subunit': [
        'python-subunit >= 1.4.3',
        'testtools >= 0.9.30',
    ],
    'docs': [
        'Sphinx',
        'sphinxcontrib-programoutput',
    ],
}


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
    license='ZPL-2.1',
    description='Zope testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires='>=3.9',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points={
        'console_scripts':
            ['zope-testrunner = zope.testrunner:run'],
    },
    include_package_data=True,
    zip_safe=False,
)
