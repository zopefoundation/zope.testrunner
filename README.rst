***************
zope.testrunner
***************

|buildstatus|_
|winbotstatus|_

.. contents::

This package provides a flexible test runner with layer support.

You can find more `detailed documentation`_ on PyPI or in the ``src/``
directory.


Getting started
***************

Buildout-based projects
=======================

zope.testrunner is often used for projects that use buildout_::

    [buildout]
    develop = .
    parts = ... test ...

    [test]
    recipe = zc.recipe.testrunner
    eggs = mypackage

The usual buildout process ::

    python bootstrap.py
    bin/buildout

creates a ``bin/test`` script that will run the tests for *mypackage*.

.. tip::

    zc.recipe.testrunner_ takes care to specify the right
    ``--test-path`` option in the generated script.  You can add
    other options (such as ``--tests-pattern``) too; check
    zc.recipe.testrunner_'s documentation for details.


Virtualenv-based projects
=========================

``pip install zope.testrunner`` and you'll get a ``zope-testrunner``
script.  Run your tests with ::

    zope-testrunner --test-path=path/to/your/source/tree

Your source code needs to be available for the testrunner to import,
so you need to run ``python setup.py install`` or ``pip install -e
.`` into the same virtualenv_.


Some useful command-line options to get you started
===================================================

-p              show a percentage indicator
-v              increase verbosity
-c              colorize the output
-t test         specify test names (one or more regexes)
-m module       specify test modules (one or more regexes)
-s package      specify test packages (one or more regexes)
--list-tests    show names of tests instead of running them
-x              stop on first error or failure
-D, --pdb       enable post-mortem debugging of test failures
--help          show *all* command-line options (there are many more!)

For example ::

    bin/test -pvc -m test_foo -t TestBar

runs all TestBar tests from a module called test_foo.py.


Writing tests
=============

``zope.testrunner`` expects to find your tests inside your package
directory, in a subpackage or module named ``tests``.  Test modules
in a test subpackage should be named ``test*.py``.

.. tip::

    You can change these assumptions with ``--tests-pattern`` and
    ``--test-file-pattern`` test runner options.

Tests themselves should be classes inheriting from
``unittest.TestCase``, and if you wish to use doctests, please tell
the test runner where to find them and what options to use for them
in by supplying a function named ``test_suite``.

Example::

    import unittest
    import doctest

    class TestArithmetic(unittest.TestCase):

        def test_two_plus_two(self):
            self.assertEqual(2 + 2, 4)


    def doctest_string_formatting():
        """Test Python string formatting

            >>> print('{} + {}'.format(2, 2))
            2 + 2

        """

    def test_suite():
        return unittest.TestSuite([
            unittest.makeSuite(TestArithmetic),
            doctest.DocTestSuite(),
            doctest.DocFileSuite('../README.txt',
                                 optionflags=doctest.ELLIPSIS),
        ])


Test grouping
=============

In addition to per-package and per-module filtering, zope.testrunner
has other mechanisms for grouping tests:

* **layers** allow you to have shared setup/teardown code to be used
  by a group of tests, that is executed only once, and not for each
  test.  Layers are orthogonal to the usual package/module structure
  and are specified by setting the ``layer`` attribute on test
  suites.

* **levels** allow you to group slow-running tests and not run them
  by default.  They're specified by setting the ``level`` attribute
  on test suites to an int.

For more details please see the `detailed documentation`_.


Other features
==============

zope.testrunner can profile your tests, measure test coverage,
check for memory leaks, integrate with subunit_, shuffle the
test execution order, and run multiple tests in parallel.

For more details please see the `detailed documentation`_.

.. _buildout: http://www.buildout.org/
.. _virtualenv: http://www.virtualenv.org/
.. _zc.recipe.testrunner: http://pypi.python.org/pypi/zc.recipe.testrunner
.. _subunit: http://pypi.python.org/pypi/subunit
.. _detailed documentation: http://docs.zope.org/zope.testrunner/

.. |buildstatus| image:: https://api.travis-ci.org/zopefoundation/zope.testrunner.png?branch=master
.. _buildstatus: https://travis-ci.org/zopefoundation/zope.testrunner

.. |winbotstatus| image:: http://winbot.zope.org/buildstatusimage?builder=zope.testrunner_py_265_32&number=-1
.. _winbotstatus: http://winbot.zope.org/builders/zope.testrunner_py_265_32/builds/-1
