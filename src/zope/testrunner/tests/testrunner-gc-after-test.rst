Debugging cyclic garbage and ResourceWarnings
=============================================

The --gc-after-test option can be used
to detect the creation of cyclic garbage and diagnose ``ResourceWarning``s.

Note: Python writes ``ResourceWarning`` messages to ``stderr``
which it not captured by ``doctest``. The sample output below
therefore does not show the warnings (even though two are issued).

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', 'gc-after-test',
    ...     ]

    >>> from zope import testrunner


    Verbosity level 1
    >>> sys.argv = 'test --gc-after-test -v'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
    .!.!.
    <BLANKLINE>
    Error in test test_exception (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
    ...
    ZeroDivisionError: ...
    <BLANKLINE>
    ...
    <BLANKLINE>
    Failure in test test_failure (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
      ...
    AssertionError: failure
    <BLANKLINE>
    ...!.!
      Ran 7 tests with 1 failures, 1 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    Tests with errors:
       test_exception (gc-after-test.GcAfterTestTests...)
    <BLANKLINE>
    Tests with failures:
       test_failure (gc-after-test.GcAfterTestTests...)

    Verbosity level 2 (or higher)
    >>> sys.argv = 'test --gc-after-test -vv'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_cycle_with_resource (gc-after-test.GcAfterTestTests...) [3]
     test_cycle_without_resource (gc-after-test.GcAfterTestTests...) [2]
     test_exception (gc-after-test.GcAfterTestTests...)
    <BLANKLINE>
    Error in test test_exception (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
      ...
    ZeroDivisionError: ...
    ...test_failure (gc-after-test.GcAfterTestTests...)
    <BLANKLINE>
    Failure in test test_failure (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
      ...
    AssertionError: failure
    ...test_okay (gc-after-test.GcAfterTestTests...)
     test_test_holds_cycle (gc-after-test.GcAfterTestTests...) [3]
     test_traceback_cycle (gc-after-test.GcAfterTestTests...) [5]
      Ran 7 tests with 1 failures, 1 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    Tests with errors:
       test_exception (gc-after-test.GcAfterTestTests...)
    <BLANKLINE>
    Tests with failures:
       test_failure (gc-after-test.GcAfterTestTests...)

    Verbosity level 4 (or higher)
    Note: starting with Python 3.13, the garbage collector identifies
    an instance and its ``__dict__``; as a consequence, cycles
    appear smaller than in preceding versions (not
    mentioning the involved ``__dict__``s).
    >>> sys.argv = 'test --gc-after-test -vvvv'.split()
    >>> _ = testrunner.run_internal(defaults)
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
     test_cycle_with_resource (gc-after-test.GcAfterTestTests...) (N.NNN s) [3]
    The following test left cyclic garbage behind:
    test_cycle_with_resource (gc-after-test.GcAfterTestTests...)
    Cycle 1
     *  ...
     test_cycle_without_resource (gc-after-test.GcAfterTestTests...) (N.NNN s) [2]
    The following test left cyclic garbage behind:
    test_cycle_without_resource (gc-after-test.GcAfterTestTests...)
    Cycle 1
     *  ...
     test_exception (gc-after-test.GcAfterTestTests...) (N.NNN s)
    <BLANKLINE>
    <BLANKLINE>
    Error in test test_exception (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
    ...
    ZeroDivisionError: ...
    ...test_failure (gc-after-test.GcAfterTestTests...) (N.NNN s)
    <BLANKLINE>
    <BLANKLINE>
    Failure in test test_failure (gc-after-test.GcAfterTestTests...)
    Traceback (most recent call last):
    ...
    AssertionError: failure
    ...test_okay (gc-after-test.GcAfterTestTests...) (N.NNN s)
     test_test_holds_cycle (gc-after-test.GcAfterTestTests...) (N.NNN s) [3]
    The following test left cyclic garbage behind:
    test_test_holds_cycle (gc-after-test.GcAfterTestTests...)
    Cycle 1
     *  ...
     test_traceback_cycle (gc-after-test.GcAfterTestTests...) (N.NNN s) [5]
    The following test left cyclic garbage behind:
    test_traceback_cycle (gc-after-test.GcAfterTestTests...)
    Cycle 1
     *  ...
      Ran 7 tests with 1 failures, 1 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    Tests with errors:
       test_exception (gc-after-test.GcAfterTestTests...)
    <BLANKLINE>
    Tests with failures:
       test_failure (gc-after-test.GcAfterTestTests...)
