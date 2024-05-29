=====================
 ``subTest`` Support
=====================

The testrunner supports ``unittest.TestCase.subTest``.

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', 'subtest',
    ...     ]

    >>> from zope import testrunner

    >>> sys.argv = 'test -vv'.split()
    >>> x = testrunner.run_internal(defaults) # doctest: +ELLIPSIS
    Running tests at level 1
    ...
      Running:
     test_subTest (subtest.TestSomething...)
    <BLANKLINE>
    Failure in test test_subTest (subtest.TestSomething...) [fail 1]
    Traceback (most recent call last):
     testrunner-ex/subtest.py", Line NNN, in test_subTest
        self.assertEqual(0, 1)
    AssertionError: 0 != 1
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    Failure in test test_subTest (subtest.TestSomething...) [fail 2]
    Traceback (most recent call last):
     testrunner-ex/subtest.py", Line NNN, in test_subTest
        self.assertEqual(0, 1)
    AssertionError: 0 != 1
    <BLANKLINE>
    <BLANKLINE>
      Ran 1 tests with 2 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    Tests with failures:
       test_subTest (subtest.TestSomething...) [fail 1]
       test_subTest (subtest.TestSomething...) [fail 2]
