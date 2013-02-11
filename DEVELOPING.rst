**************************
developing zope.testrunner
**************************

Zope testrunner needs itself to run it's own tests. There are two ways to 
do that.

Note: At the moment of writing buildout does not support Python 3, and
therefore you must use the latter way of running the tests in Python 3.
Also, the zc.recipe.testrunner doesn't yet support zope.testrunner, so 
actually, the first way doesn't work unless you manually edit bin/test.


Using zc.buildout
-----------------

The standard way to set up a testrunner to test zope.testrunner with,
is to use buildout::

    # python bootstrap.py
    # bin/buildout

You can now run the tests:
    
    # bin/test
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
      Ran 27 tests with 0 failures and 0 errors in 17.384 seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.    
    
Using setup.py
--------------

You may run the tests without buildout as well, as the setup.py has
a custom test command that will run the tests:

    # python setup.py test
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

