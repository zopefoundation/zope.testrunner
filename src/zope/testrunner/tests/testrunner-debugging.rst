=========================
 Debugging Test Failures
=========================

The testrunner module supports post-mortem debugging and debugging
using `pdb.set_trace`. Let's look first at using `pdb.set_trace`. To
demonstrate this, we'll provide input via helper Input objects:

    >>> class Input:
    ...     def __init__(self, src):
    ...         self.lines = src.split('\n')
    ...     def readline(self):
    ...         line = self.lines.pop(0)
    ...         print(line)
    ...         return line+'\n'

If a test or code called by a test calls pdb.set_trace, then the
runner will enter pdb at that point:

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

    >>> real_stdin = sys.stdin
    >>> sys.stdin = Input('p x\nc')

    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace1').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
    ...
    > testrunner-ex/sample3/sampletests_d.py(27)test_set_trace1()
    -> ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.001 seconds.
    ...
    False

Post-Mortem Debugging
=====================

You can also do post-mortem debugging, using the --post-mortem (-D)
option:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem1 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE +REPORT_NDIFF +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
    ...
    Error in test test_post_mortem1 (sample3.sampletests_d.TestSomething...)
    Traceback (most recent call last):
      File "testrunner-ex/sample3/sampletests_d.py",
              line 34, in test_post_mortem1
        raise ValueError
    ValueError
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(34)test_post_mortem1()
    -> raise ValueError
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Note that the test runner exits after post-mortem debugging.

In the example above, we debugged an error. Failures are actually
converted to errors and can be debugged the same way:

    >>> sys.stdin = Input('p x\np y\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem_failure1 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE +REPORT_NDIFF +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
    ...
    Error in test test_post_mortem_failure1 (sample3.sampletests_d.TestSomething...)
    Traceback (most recent call last):
      File ".../unittest.py",  line 252, in debug
        getattr(self, self.__testMethodName)()
      File "testrunner-ex/sample3/sampletests_d.py",
        line 42, in test_post_mortem_failure1
        assert x == y
    AssertionError
    <BLANKLINE>
    ...AssertionError
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(42)test_post_mortem_failure1()
    -> assert x == y
    (Pdb) p x
    1
    (Pdb) p y
    2
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Skipping tests with ``@unittest.skip`` decorator does not trigger the
post-mortem debugger:

    >>> sys.stdin = Input('q')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t skipped -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE +REPORT_NDIFF +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 1 tests with 0 failures, 0 errors and 1 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Tests marked as expected failures with the ``@unittest.expectedFailure`` decorator do
not trigger the post-mortem debugger when they fail as expected:

    >>> expected_failure_tests_defaults = [
    ...     '--path', os.path.join(this_directory, 'testrunner-ex-expectedFailure'),
    ...     '--tests-pattern', '^sample_expected_failure_tests$',
    ...     ]
    >>> sys.stdin = Input('q')
    >>> sys.argv = 'test -t test_expected_failure -D'.split()
    >>> try: testrunner.run_internal(expected_failure_tests_defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE +REPORT_NDIFF +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

When ``@unittest.expectedFailure`` test unexpectedly pass, it's not possible to use
the post-mortem debugger, because no exception was raised. In that case a warning is
printed:

    >>> sys.stdin = Input('q')
    >>> sys.argv = 'test -t test_unexpected_success -D'.split()
    >>> try: testrunner.run_internal(expected_failure_tests_defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE +REPORT_NDIFF +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Error in test test_unexpected_success (sample_expected_failure_tests.TestExpectedFailures...)
      Traceback (most recent call last):
      zope.testrunner.runner.UnexpectedSuccess
      **********************************************************************
      Can't post-mortem debug an unexpected success
      **********************************************************************
      Ran 1 tests with 1 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    True
