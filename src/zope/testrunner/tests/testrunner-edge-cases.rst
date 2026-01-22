testrunner Edge Cases
=====================

This document has some edge-case examples to test various aspects of
the test runner.

Separating Python path and test directories
-------------------------------------------

The --path option defines a directory to be searched for tests *and* a
directory to be added to Python's search path.  The --test-path option
can be used when you want to set a test search path without also
affecting the Python path:

    >>> import os, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')

    >>> from zope import testrunner

    >>> defaults = [
    ...     '--test-path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]
    >>> sys.argv = ['test']
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Test-module import failures:
    <BLANKLINE>
    Module: sampletestsf
    <BLANKLINE>
    Traceback (most recent call last):
    ModuleNotFoundError: No module named 'sampletestsf'
    ...

    >>> sys.path.append(directory_with_tests)
    >>> sys.argv = ['test']
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 156 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Running samplelayers.Layer1 tests:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
      Set up samplelayers.Layer1 in 0.000 seconds.
      Ran 9 tests with 0 failures, 0 errors and 0 skipped in 0.000 seconds.
    ...
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in N.NNN seconds.
      Tear down samplelayers.Layer12 in N.NNN seconds.
      Tear down samplelayers.Layer1 in N.NNN seconds.
    Total: 321 tests, 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    False

Bug #251759: The test runner's protection against descending into non-package
directories was ineffective, e.g. picking up tests from eggs that were stored
close by:

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex-251759')

    >>> defaults = [
    ...     '--test-path', directory_with_tests,
    ...     ]
    >>> testrunner.run_internal(defaults)
    Total: 0 tests, 0 failures, 0 errors and 0 skipped in 0.000 seconds.
    False

Test Suites with None for suites or tests
-----------------------------------------

    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--test-path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]
    >>> sys.argv = ['test',
    ...             '--tests-pattern', '^sampletests_none_suite$',
    ...     ]
    >>> testrunner.run_internal(defaults)
    Test-module import failures:
    <BLANKLINE>
    Module: sample1.sampletests_none_suite
    <BLANKLINE>
    Traceback (most recent call last):
    TypeError: Invalid test_suite, None, in sample1.sampletests_none_suite
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    Test-modules with import problems:
      sample1.sampletests_none_suite
    Total: 0 tests, 0 failures, 1 errors and 0 skipped in N.NNN seconds.
    True


    >>> sys.argv = ['test',
    ...             '--tests-pattern', '^sampletests_none_test$',
    ...     ]
    >>> testrunner.run_internal(defaults)
    Test-module import failures:
    <BLANKLINE>
    Module: sample1.sampletests_none_test
    <BLANKLINE>
    Traceback (most recent call last):
    TypeError: ...
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    Test-modules with import problems:
      sample1.sampletests_none_test
    Total: 0 tests, 0 failures, 1 errors and 0 skipped in N.NNN seconds.
    True

You must use --repeat with --report-refcounts
---------------------------------------------

It is an error to specify --report-refcounts (-r) without specifying a
repeat count greater than 1

    >>> sys.argv = 'test -r'.split()
    >>> testrunner.run_internal(defaults)
            You must use the --repeat (-N) option to specify a repeat
            count greater than 1 when using the --report_refcounts (-r)
            option.
    <BLANKLINE>
    True

    >>> sys.argv = 'test -r -N1'.split()
    >>> testrunner.run_internal(defaults)
            You must use the --repeat (-N) option to specify a repeat
            count greater than 1 when using the --report_refcounts (-r)
            option.
    <BLANKLINE>
    True


Selection
---------

Several tests can be excluded using the '!' notation:

    >>> sys.argv = 'test -u -vv -ssample1.sample13 -t!test_x -t!test_y'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_z0 (sample1.sample13.sampletests.TestA...)
     test_z0 (sample1.sample13.sampletests.TestB...)
     test_1 (sample1.sample13.sampletests.TestNotMuch...)
     test_2 (sample1.sample13.sampletests.TestNotMuch...)
     test_3 (sample1.sample13.sampletests.TestNotMuch...)
     test_z1 (sample1.sample13.sampletests)
     testrunner-ex/sample1/sample13/../../sampletests.rst
      Ran 7 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Requiring unique test IDs
-------------------------

The --require-unique option causes the test runner to require that all test
IDs be unique.  Its behaviour is tested in zope.testrunner.tests.test_find;
here we check its interaction with other options.

The --require-unique option does not issue any warnings on its own.

    >>> sys.argv = 'test --require-unique'.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
    ...

Attempting to use both --module and --require-unique issues a warning.

    >>> sys.argv = 'test --module sample --require-unique'.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    You specified a module along with --require-unique;
    --require-unique will not try to enforce test ID uniqueness when
    working with a specific module.
    Running zope.testrunner.layer.UnitTests tests:
    ...
