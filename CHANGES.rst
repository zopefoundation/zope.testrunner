zope.testrunner Changelog
*************************

4.6.0 (2016-12-28)
==================

- Make the ``subunit`` support purely optional: applications which have
  been getting the dependencies via ``zope.testrunner`` should either add
  ``zope.testrunner[subunit]`` to their ``install_requires`` or else
  depend directly on ``python-subunit``.

- New option ``--ignore-new-thread=<regexp>`` to suppress "New thread(s)"
  warnings.

- Support Python 3.6.


4.5.1 (2016-06-20)
==================

- Fixed: Using the ``-j`` option to run tests in multiple processes
  caused tests that used the ``multiprocessing`` package to hang
  (because the testrunner replaced ``sys.stdin`` with an unclosable
  object).

- Drop conditional dependency on ``unittest2`` (redundant after dropping
  support for Python 2.6).


4.5.0 (2016-05-02)
==================

- Stop tests for all layers when test fails/errors when started with
  -x/--stop-on-error
  (`#37 <https://github.com/zopefoundation/zope.testrunner/pull/37>`_).

- Drop support for Python 2.6 and 3.2.


4.4.10 (2015-11-10)
===================

- Add support for Python 3.5
  (`#31 <https://github.com/zopefoundation/zope.testrunner/pull/31>`_).

- Insert extra paths (from ``--path``) to the front of sys.argv
  (`#32 <https://github.com/zopefoundation/zope.testrunner/issues/32>`_).


4.4.9 (2015-05-21)
==================

- When using ``-j``, parallelize all the tests, including the first test layer
  (`#28 <https://github.com/zopefoundation/zope.testrunner/issues/28>`_).


4.4.8 (2015-05-01)
==================

- Support skipped tests in subunit output
  (`#25 <https://github.com/zopefoundation/zope.testrunner/pull/25>`_).

- More efficient test filtering
  (`#26 <https://github.com/zopefoundation/zope.testrunner/pull/26>`_).


4.4.7 (2015-04-02)
==================

- Work around a bug in PyPy3's curses module
  (`#24 <https://github.com/zopefoundation/zope.testrunner/issues/24>`_).


4.4.6 (2015-01-21)
==================

- Restore support for instance-based test layers that regressed in 4.4.5
  (`#20 <https://github.com/zopefoundation/zope.testrunner/pull/20>`_).


4.4.5 (2015-01-06)
==================

- Sort related layers close to each other to reduce the number of unnecessary
  teardowns (fixes `#14
  <https://github.com/zopefoundation/zope.testrunner/issues/14>`_).

- Run the unit test layer first (fixes `LP #497871
  <https://bugs.launchpad.net/zope.testrunner/+bug/497871>`__).


4.4.4 (2014-12-27)
==================

- When looking for the right location of test code, start with longest
  location paths first. This fixes problems with nested code locations.


4.4.3 (2014-03-19)
==================

- Added support for Python 3.4.


4.4.2 (2014-02-22)
==================

- Drop support for Python 3.1.

- Fix post-mortem debugging when a non-printable exception happens
  (https://github.com/zopefoundation/zope.testrunner/issues/8).


4.4.1 (2013-07-10)
==================

- Updated ``boostrap.py`` to version 2.2.

- Fix nondeterministic test failures on Python 3.3

- Tear down layers after ``post_mortem`` debugging is finished.

- Fix tests that write to source directory, it might be read-only.


4.4.0 (2013-06-06)
==================

- Fix tests selection when the negative "!" pattern is used several times
  (LP #1160965)

- Moved tests into a 'tests' subpackage.

- Made ``python -m zope.testrunner`` work again.

- Support 'skip' feature of unittest2 (which became the new unittest in Python
  2.7).

- Better diagnostics when communication with subprocess fails
  (https://github.com/zopefoundation/zope.testrunner/issues/5).

- Do not break subprocess execution when the test suite changes the working
  directory (https://github.com/zopefoundation/zope.testrunner/issues/6).

- Count test module import errors as errors (LP #1026576).


4.3.3 (2013-03-03)
==================

- Running layers in sub-processes did not use to work when run via
  ``python setup.py ftest`` since it tried to run setup.py with all the
  command line options. It now detects ``setup.py`` runs and we run the test
  runner directly.


4.3.2 (2013-03-03)
==================

- Fix ``SkipLayers`` class in cases where the distribution specifies a
  ``test_suite`` value.


4.3.1 (2013-03-02)
==================

- Fixed a bug in the `ftest` command and added a test.

- Fixed a trivial test failure with Python 3 of the previous release.


4.3.0 (2013-03-02)
==================

- Expose `ftest` distutils command via an entry point.

- Added tests for ``zope.testrunner.eggsupport``.


4.2.0 (2013-02-12)
==================

- Dropped use of 2to3, rewrote source code to be compatible with all Python
  versions.  Introduced a dependency on `six`_.


4.1.1 (2013-02-08)
==================

- Dropped use of zope.fixers (LP: #1118877).

- Fixed tox test error reporting; fixed tests on Pythons 2.6, 3.1, 3.2, 3.3 and
  PyPy 1.9.

- Fix --shuffle ordering on Python 3.2 to be the same as it was on older Python
  versions.

- Fix --shuffle nondeterminism when multiple test layers are present.
  Note: this will likely change the order of tests for the same --shuffle-seed.

- New option: --profile-directory.  Use it in the test suite so that tests
  executed by detox in parallel don't conflict.

- Use a temporary coverage directory in the test suite so that tests
  executed by detox in parallel don't conflict.

- Fix --post-mortem (aka -D, --pdb) when a test module cannot be imported
  or is invalid (LP #1119363).


4.1.0 (2013-02-07)
==================

- Replaced deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Dropped support for Python 2.4 and 2.5.

- Made StartUpFailure compatible with unittest.TextTestRunner() (LP #1118344).


4.0.4 (2011-10-25)
==================

- Work around sporadic timing-related issues in the subprocess buffering
  tests.  Thanks to Jonathan Ballet for the patch!


4.0.3 (2011-03-17)
==================

- Added back support for Python <= 2.6 which was broken in 4.0.2.


4.0.2 (2011-03-16)
==================

- Added back Python 3 support which was broken in 4.0.1.

- Fixed `Unexpected success`_ support by implementing the whole concept.

- Added support for the new __pycache__ directories in Python 3.2.


4.0.1 (2011-02-21)
==================

- LP #719369: An `Unexpected success`_ (concept introduced in Python 2.7) is
  no longer handled as success but as failure. This is a workaround. The
  whole unexpected success concept might be implemented later.

.. _`Unexpected success`: http://www.voidspace.org.uk/python/articles/unittest2.shtml#more-skipping


4.0.0 (2010-10-19)
==================

- Show more information about layers whose setup fails (LP #638153).


4.0.0b5 (2010-07-20)
====================

- Update fix for LP #221151 to a spelling compatible with Python 2.4.

- Timestamps are now always included in subunit output (r114849).

- LP #591309: fix a crash when subunit reports test failures containing
  UTF8-encoded data.


4.0.0b4 (2010-06-23)
====================

- Package as a zipfile to work around Python 2.4 distutils bug (no
  feature changes or bugfixes in ``zope.testrunner`` itself).


4.0.0b3 (2010-06-16)
====================

- LP #221151: keep ``unittest.TestCase.shortDescription`` happy by supplying
  a ``_testMethodDoc`` attribute.

- LP #595052: keep the distribution installable under Python 2.4:  its
  distutils appears to munge the empty ``__init__.py`` file in the
  ``foo.bar`` egg used for testing into a directory.

- LP #580083: fix the ``bin/test`` script to run only tests from
  ``zope.testrunner``.

- LP #579019: When layers were run in parallel, their tearDown was
  not called. Additionally, the first layer which was run in the main
  thread did not have its tearDown called either.


4.0.0b2 (2010-05-03)
====================

- Having 'sampletests' in the MANIFEST.in gave warnings, but doesn't actually
  seem to include any more files, so I removed it.

- Moved zope.testing.exceptions to zope.testrunner.exceptions. Now
  zope.testrunner no longer requires zope.testing except for when running
  its own tests.


4.0.0b1 (2010-04-29)
====================

- Initial release of the testrunner from zope.testrunner as its own module.
  (Previously it was part of zope.testing.)


.. _six: http://pypi.python.org/pypi/six
