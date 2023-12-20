==========
XML report
==========

By default, ``zope.testrunner`` reports the results to the terminal.
CI systems however, need a machine readable format
to actually parse the results and display them.

The ``JUnit`` package from the Java community, long ago,
created an XML report format that since then every CI system is able to read.

The ``--xml`` option tells the test runner to produce such a report.

    >>> from pathlib import Path
    >>> import sys
    >>> directory_with_tests = Path(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', str(directory_with_tests),
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

    >>> from zope import testrunner
    >>> default_argv = 'test -u --xml -t sample3'.split()

Run tests
=========

Ensure no leftovers from previous runs are there:

    >>> reports_folder = Path('testreports')
    >>> if reports_folder.exists():
    ...     _ = [x.unlink() for x in reports_folder.iterdir()]
    ...     _ = reports_folder.rmdir()

Run the tests:

    >>> testrunner.run_internal(defaults, default_argv)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 13 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False

A report has been created:

    >>> reports_folder.exists()
    True

There are 5 reports:

    >>> reports = [x for x in reports_folder.iterdir()]
    >>> len(reports)
    5

Report details
==============

Let's look at an individual report.

It's an XML file:

    >>> report = reports_folder / 'sample3.sampletests.TestA.xml'

3 tests were run with no errors nor failures:

    >>> content = report.read_text()
    >>> ' tests="3" ' in content
    True
    >>> ' errors="0" ' in content
    True
    >>> ' failures="0" ' in content
    True

The specific tests that were run:

    >>> '<testcase classname="sample3.sampletests.TestA" name="test_x1"' in content
    True
    >>> '<testcase classname="sample3.sampletests.TestA" name="test_y0"' in content
    True
    >>> '<testcase classname="sample3.sampletests.TestA" name="test_z0"' in content
    True

Remove the files:

    >>> _ = [x.unlink() for x in reports_folder.iterdir()]
    >>> _ = reports_folder.rmdir()

Errors reported
===============

If errors/failures happen, they are also reported in the XML files:

.. note::
    Code copied from ``testrunner-errors.rst``

    >>> import os.path, sys, tempfile, shutil
    >>> tmpdir = tempfile.mkdtemp()
    >>> directory_with_tests = os.path.join(tmpdir, 'testrunner-ex')
    >>> source = os.path.join(this_directory, 'testrunner-ex')
    >>> n = len(source) + 1
    >>> for root, dirs, files in os.walk(source):
    ...     dirs[:] = [d for d in dirs if d != ".svn"] # prune cruft
    ...     os.mkdir(os.path.join(directory_with_tests, root[n:]))
    ...     for f in files:
    ...         _ = shutil.copy(os.path.join(root, f),
    ...                         os.path.join(directory_with_tests, root[n:], f))

    >>> from zope import testrunner
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     '--xml',
    ...     ]

    >>> sys.argv = 'test --tests-pattern ^sampletests(f|_e|_f)?$ '.split()
    >>> testrunner.run_internal(defaults)
    ... # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    Running zope.testrunner.layer.UnitTests tests:
    ...
    Total: 329 tests, 3 failures, 1 errors and 0 skipped in N.NNN seconds.
    True

Let's look at the XML reports:

    >>> reports_folder.exists()
    True

There are quite some reports:

    >>> len([x for x in reports_folder.iterdir()])
    106

Report details
==============

Let's look at an individual report.

It's an XML file:

    >>> report = reports_folder / 'sample2.sampletests_e.Test.xml'
    >>> report.exists()
    True

Let's see the stats:

    >>> content = report.read_text()
    >>> ' tests="5" ' in content
    True
    >>> ' errors="1" ' in content
    True
    >>> ' failures="0" ' in content
    True

Errors
------

The error message is reported:

    >>> '<error message="name \'y\' is not defined"' in content
    True

And the traceback is there as well:

    >>> 'sampletests_e.py", line 47, in test3' in content
    True

Failures
--------

    >>> report = reports_folder / 'doctest-src-zope-testrunner-tests-testrunner-ex-sample2-e.rst.xml'
    >>> report.exists()
    True

Let's see the stats:

    >>> content = report.read_text()
    >>> ' tests="1" ' in content
    True
    >>> ' errors="0" ' in content
    True
    >>> ' failures="1" ' in content
    True

The failure is reported:

    >>> 'Exception raised:' in content
    True

Remove the files:

    >>> _ = [x.unlink() for x in reports_folder.iterdir()]
    >>> _ = reports_folder.rmdir()
