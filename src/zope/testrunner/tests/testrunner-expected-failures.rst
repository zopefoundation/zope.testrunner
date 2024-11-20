testrunner handling of expected failures
========================================

    >>> import os, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex-expectedFailure')

    >>> from zope import testrunner

    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sample_expected_failure_tests$',
    ...     ]

Expected failures are not reported as failures:

    >>> sys.argv = 'test -t test_expected_failure'.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Unexpected successes are reported as failures:

    >>> sys.argv = 'test -t test_unexpected_success'.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    <BLANKLINE>
    Error in test test_unexpected_success (sample_expected_failure_tests.TestExpectedFailures...)
    Traceback (most recent call last):
      zope.testrunner.runner.UnexpectedSuccess
    <BLANKLINE>
      Ran 1 tests with 1 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    True

In verbose mode, tests with unexpected failures are listed as failures in the summary:

    >>> sys.argv = 'test -t test_unexpected_success -vv'.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +ELLIPSIS
    Running tests at level 1
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
      test_unexpected_success (sample_expected_failure_tests.TestExpectedFailures...)
    Error in test test_unexpected_success (sample_expected_failure_tests.TestExpectedFailures...)
    Traceback (most recent call last):
    zope.testrunner.runner.UnexpectedSuccess
      Ran 1 tests with 1 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    Tests with failures:
      test_unexpected_success (sample_expected_failure_tests.TestExpectedFailures...)
    <BLANKLINE>
    True
