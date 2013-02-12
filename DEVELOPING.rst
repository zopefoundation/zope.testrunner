**************************
developing zope.testrunner
**************************

Zope testrunner needs itself to run its own tests. There are two ways to
do that.


Using zc.buildout
-----------------

The standard way to set up a testrunner to test zope.testrunner with,
is to use buildout::

    $ python bootstrap.py
    $ bin/buildout

You can now run the tests::

    $ bin/test -pvc
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.000 seconds.

      Ran 28 tests with 0 failures and 0 errors in 17.384 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.



Using setup.py
--------------

You may run the tests without buildout as well, as the setup.py has
a custom test command that will run the tests::

    $ python setup.py test
    running test
    running egg_info
    writing requirements to src/zope.testrunner.egg-info/requires.txt
    writing src/zope.testrunner.egg-info/PKG-INFO
    writing namespace_packages to src/zope.testrunner.egg-info/namespace_packages.txt
    writing top-level names to src/zope.testrunner.egg-info/top_level.txt
    writing dependency_links to src/zope.testrunner.egg-info/dependency_links.txt
    writing entry points to src/zope.testrunner.egg-info/entry_points.txt
    reading manifest template 'MANIFEST.in'
    warning: no files found matching 'sampletests' under directory 'src'
    writing manifest file 'src/zope.testrunner.egg-info/SOURCES.txt'
    running build_ext
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
      Ran 27 tests with 0 failures and 0 errors in 17.600 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.


Using tox/detox
---------------

This is a convenient way to run the test suite for all supported Python
versions, either sequentially (`tox`_) or in parallel (`detox`_)::

    $ detox
    GLOB sdist-make: /home/mg/src/zope.testrunner/setup.py
    py33 sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    py27 sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    pypy sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    py31 sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    py32 sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    py26 sdist-reinst: .../.tox/dist/zope.testrunner-4.1.2.dev0.zip
    py27 runtests: commands[0]
    py26 runtests: commands[0]
    pypy runtests: commands[0]
    py32 runtests: commands[0]
    py33 runtests: commands[0]
    py31 runtests: commands[0]
    ______________________________ summary _______________________________
      py26: commands succeeded
      py27: commands succeeded
      py31: commands succeeded
      py32: commands succeeded
      py33: commands succeeded
      pypy: commands succeeded
      congratulations :)

.. _tox: http://pypi.python.org/pypi/tox
.. _detox: http://pypi.python.org/pypi/detox
