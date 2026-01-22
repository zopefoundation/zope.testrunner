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


Debugging Edge Cases
====================

    >>> defaults = [
    ...     '--test-path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]
    >>> class Input:
    ...     def __init__(self, src):
    ...         self.lines = src.split('\n')
    ...     def readline(self):
    ...         line = self.lines.pop(0)
    ...         print(line)
    ...         return line+'\n'

    >>> real_stdin = sys.stdin

Using pdb.set_trace in a function called by an ordinary test:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace2').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:...
    > testrunner-ex/sample3/sampletests_d.py(47)f()
    -> ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in 0.001 seconds.
    ...
    False

Using pdb.set_trace in a function called by a doctest in a doc string:

    >>> sys.stdin = Input('n\np x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace4').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    > testrunner-ex/sample3/sampletests_d.py(NNN)f()
    -> ...
    (Pdb) n
    ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Using pdb in a docstring-based doctest

    >>> sys.stdin = Input('n\np x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace3').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    ...
    (Pdb) n
    ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Using pdb.set_trace in a doc file:


    >>> sys.stdin = Input('n\np x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace5').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    ...
    (Pdb) n
    ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Using pdb.set_trace in a function called by a doctest in a doc file:


    >>> sys.stdin = Input('n\np x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t set_trace6').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    ...
    (Pdb) n
    ...
    (Pdb) p x
    1
    (Pdb) c
      Ran 1 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Post-mortem debugging function called from ordinary test:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem2 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:...
    <BLANKLINE>
    <BLANKLINE>
    Error in test test_post_mortem2 (sample3.sampletests_d.TestSomething...)
    Traceback (most recent call last):
      File "testrunner-ex/sample3/sampletests_d.py",
           line 37, in test_post_mortem2
        g()
      File "testrunner-ex/sample3/sampletests_d.py", line 46, in g
        raise ValueError
    ValueError
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(46)g()
    -> raise ValueError
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Post-mortem debugging docstring-based doctest:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem3 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    <BLANKLINE>
    Error in test post_mortem3 (sample3.sampletests_d)
    Traceback (most recent call last):
    ...UnexpectedException: testrunner-ex/sample3/sampletests_d.py:NNN (2 examples)>
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > <doctest sample3.sampletests_d.post_mortem3[1]>(1)?()
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Post-mortem debugging function called from docstring-based doctest:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem4 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    <BLANKLINE>
    Error in test post_mortem4 (sample3.sampletests_d)
    Traceback (most recent call last):
    ...UnexpectedException: testrunner-ex/sample3/sampletests_d.py:NNN (1 example)>
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(NNN)g()
    -> raise ValueError
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Post-mortem debugging file-based doctest:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem5 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    <BLANKLINE>
    Error testrunner-ex/sample3/post_mortem5.rst
    Traceback (most recent call last):
    ...UnexpectedException: testrunner-ex/sample3/post_mortem5.rst:0 (2 examples)>
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > <doctest post_mortem5.rst[1]>(1)?()
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False



Post-mortem debugging function called from file-based doctest:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem6 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:...
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
    <BLANKLINE>
    <BLANKLINE>
    Error testrunner-ex/sample3/post_mortem6.rst
    Traceback (most recent call last):
      File ".../zope/testing/doctest/__init__.py", Line NNN, in debug
        runner.run(self._dt_test, clear_globs=False)
      File ".../zope/testing/doctest/__init__.py", Line NNN, in run
        r = DocTestRunner.run(self, test, compileflags, out, False)
      File ".../zope/testing/doctest/__init__.py", Line NNN, in run
        return self.__run(test, compileflags, out)
      File ".../zope/testing/doctest/__init__.py", Line NNN, in __run
        exc_info)
      File ".../zope/testing/doctest/__init__.py", Line NNN, in report_unexpected_exception
        raise UnexpectedException(test, example, exc_info)
    ...UnexpectedException: testrunner-ex/sample3/post_mortem6.rst:0 (2 examples)>
    <BLANKLINE>
    ...ValueError
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(NNN)g()
    -> raise ValueError
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Post-mortem debugging of a docstring doctest failure:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem_failure2 -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:...
    <BLANKLINE>
    <BLANKLINE>
    Error in test post_mortem_failure2 (sample3.sampletests_d)
    <BLANKLINE>
    File "testrunner-ex/sample3/sampletests_d.py",
                   line 81, in sample3.sampletests_d.post_mortem_failure2
    <BLANKLINE>
    x
    <BLANKLINE>
    Want:
    2
    <BLANKLINE>
    Got:
    1
    <BLANKLINE>
    <BLANKLINE>
    > testrunner-ex/sample3/sampletests_d.py(81)_()
    ...ValueError: Expected and actual output are different
    > <string>(1)...()
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Post-mortem debugging of a docfile doctest failure:

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = ('test -ssample3 --tests-pattern ^sampletests_d$'
    ...             ' -t post_mortem_failure.rst -D').split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    ... # doctest: +NORMALIZE_WHITESPACE
    Running zope.testrunner.layer.UnitTests tests:...
    <BLANKLINE>
    <BLANKLINE>
    Error in test /home/jim/z3/zope.testrunner/src/zope/testing/testrunner-ex/sample3/post_mortem_failure.rst
    <BLANKLINE>
    File "testrunner-ex/sample3/post_mortem_failure.rst",
                                      line 2, in post_mortem_failure.rst
    <BLANKLINE>
    x
    <BLANKLINE>
    Want:
    2
    <BLANKLINE>
    Got:
    1
    <BLANKLINE>
    <BLANKLINE>
    > testrunner-ex/sample3/post_mortem_failure.rst(2)_()
    ...ValueError:
    Expected and actual output are different
    > <string>(1)...()
    (Pdb) p x
    1
    (Pdb) c
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

Post-mortem debugging with triple verbosity

    >>> sys.stdin = Input('p x\nc')
    >>> sys.argv = 'test --layer samplelayers.Layer1$ -vvv -D'.split()
    >>> try: testrunner.run_internal(defaults)
    ... finally: sys.stdin = real_stdin
    Running tests at level 1
    Running samplelayers.Layer1 tests:
      Set up samplelayers.Layer1 in 0.000 seconds.
      Running:
        test_x1 (sampletestsf.TestA1...) (0.000 s)
        test_y0 (sampletestsf.TestA1...) (0.000 s)
        test_z0 (sampletestsf.TestA1...) (0.000 s)
        test_x0 (sampletestsf.TestB1...) (0.000 s)
        test_y1 (sampletestsf.TestB1...) (0.000 s)
        test_z0 (sampletestsf.TestB1...) (0.000 s)
        test_1 (sampletestsf.TestNotMuch1...) (0.000 s)
        test_2 (sampletestsf.TestNotMuch1...) (0.000 s)
        test_3 (sampletestsf.TestNotMuch1...) (0.000 s)
      Ran 9 tests with 0 failures, 0 errors and 0 skipped in 0.001 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer1 in 0.000 seconds.
    False
