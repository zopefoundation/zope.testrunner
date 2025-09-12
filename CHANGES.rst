===========================
 zope.testrunner Changelog
===========================

8.0 (2025-09-12)
================

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


7.4 (2025-05-28)
================

- Add ``--auto-path`` option.
  This automatically adds the path of all packages from the ``--package`` option to the test paths.
  (`#198 <https://github.com/zopefoundation/zope.testrunner/pull/198>`_)


7.3 (2025-05-15)
================

- Improve ``@unittest.expectedFailure`` support, especially regarding
  post-mortem debugger. (`#196 <https://github.com/zopefoundation/zope.testrunner/pull/196>`_)


7.2 (2025-03-06)
================

- Re-add a single import of ``pkg_resources`` to avoid other import issues in
  mixed pip/buildout environments.
  (`#194 <https://github.com/zopefoundation/zope.testrunner/issues/194>`_)


7.1 (2025-03-05)
================

- Replace ``pkg_resources`` with ``importlib.metadata``.


7.0 (2025-02-12)
================

Backwards-incompatible changes
------------------------------

- Remove ``setup.py ftest`` command.
  (`#178 <https://github.com/zopefoundation/zope.testrunner/issues/178>`_)

- Remove ``zope.testrunner.eggsupport``.  It is no longer usable as of
  ``setuptools`` 72.0.0.
  (`#185 <https://github.com/zopefoundation/zope.testrunner/issues/185>`_)


6.7 (2025-02-07)
================

- Drop support for Python 3.8.

- Add option ``--only-level=level`` to run tests only at the specified level.
  (`#188 <https://github.com/zopefoundation/zope.testrunner/issues/188>`_)


6.6.1 (2024-12-13)
==================

- Make signatures in ``tb_format`` Python 3.12+ compatible
  (`#186 <https://github.com/zopefoundation/zope.testrunner/issues/186>`_)


6.6 (2024-10-16)
================

- Make tests compatible with Python 3.13 + add support for that version.
  (`#181 <https://github.com/zopefoundation/zope.testrunner/pull/181>`_)

- Drop support for Python 3.7.


6.5 (2024-08-06)
================

- Remove setuptools fossils.

- ``unittest.TestCase.subTest`` support
  (`#91 <https://github.com/zopefoundation/zope.testrunner/issues/91>`_).

- remove support for ``setup.py``'s ``test`` command.
  Support for this command has been dropped by modern
  ``setuptools`` versions and correspondingly has been removed from
  most ``zopefoundation`` packages; ``zope.testrunner`` now follows.

- ``setup.py``'s ``ftest`` command is now only supported
  when the used ``setuptools`` version still supports ``test``.


6.4 (2024-02-27)
================

- Add PEP 420 support (implicit namespaces).
  (`#160 <https://github.com/zopefoundation/zope.testrunner/issues/160>`_)


6.3.1 (2024-02-12)
==================

- Fix XML tests when running in distribution resp. separately.
  (`#163 <https://github.com/zopefoundation/zope.testrunner/issues/163>`_)


6.3 (2024-02-07)
================

- Exit cleanly when using the test runner ``--version`` argument.
  (`#102 <https://github.com/zopefoundation/zope.testrunner/issues/102>`_)

- Add new ``--xml <path>`` option to write JUnit-like XML reports.
  Code comes from ``collective.xmltestreport``, but be aware that here ``--xml``
  is not a boolean, but expects a path!
  (`#148 <https://github.com/zopefoundation/zope.testrunner/issues/148>`_).

- Add support for Python 3.13a3.


6.2.1 (2023-12-22)
==================

- Work around Python 3.12.1+ no longer calling ``startTest`` for skipped tests
  (`#157 <https://github.com/zopefoundation/zope.testrunner/issues/157>`_).


6.2 (2023-11-08)
================

- Add support for Python 3.12.

- Update code and tests to ``python-subunit >= 1.4.3`` thus requiring at least
  this version.


6.1 (2023-08-26)
================

- Add preliminary support for Python 3.12b4.
  (`#149 <https://github.com/zopefoundation/zope.testrunner/issues/149>`_)


6.0 (2023-03-28)
================

- Drop support for Python 2.7, 3.5, 3.6.


5.6 (2022-12-09)
================

- Add support for Python 3.11.

- Inline a small part of ``random.Random.shuffle`` which was deprecated in
  Python 3.9 and removed in 3.11 (`#119
  <https://github.com/zopefoundation/zope.testrunner/issues/119>`_).

- Don't trigger post mortem debugger for skipped tests. ( `#141
  <https://github.com/zopefoundation/zope.testrunner/issues/141>`_).


5.5.1 (2022-09-07)
==================

- Fix: let ``--at-level=level`` with ``level <= 0`` run the tests
  at all levels (rather than at no level)
  `#138 <https://github.com/zopefoundation/zope.testrunner/issues/138>`_.


5.5 (2022-06-24)
================

- Use ``sys._current_frames`` (rather than ``threading.enumerate``)
  as base for new thread detection, fixes
  `#130 <https://github.com/zopefoundation/zope.testrunner/issues/130>`_.

- New option ``--gc-after-test``. It calls for a garbage collection
  after each test and can be used to track down ``ResourceWarning``s
  and cyclic garbage.
  With ``rv = gc.collect()``, ``!`` is output on verbosity level 1 when
  ``rv`` is non zero (i.e. when cyclic structures have been released),
  ``[``*rv*``]`` on higher verbosity levels and
  a detailed cyclic garbage analysis on verbosity level 4+.
  For details, see
  `#133 <https://github.com/zopefoundation/zope.testrunner/pull/133>`_.

- Allow the filename for the logging configuration to be specified
  via the envvar ``ZOPE_TESTRUNNER_LOG_INI``.
  If not defined, the configuration continues to be locked for
  in file ``log.ini`` of the current working directory.
  Remember the logging configuration file in envvar
  ``ZOPE_TESTRUNNER_LOG_INI`` to allow spawned child processes
  to recreate the logging configuration.
  For details, see
  `#134 <https://github.com/zopefoundation/zope.testrunner/pull/134>`_.


5.4.0 (2021-11-19)
==================

- Improve ``--help`` documentation for ``--package-path`` option
  (`#121 <https://github.com/zopefoundation/zope.testrunner/pull/121>`_).

- Do not disable existing loggers during logsupport initialization
  (`#120 <https://github.com/zopefoundation/zope.testrunner/pull/120>`_).

- Fix tests with testtools >= 2.5.0 (`#125
  <https://github.com/zopefoundation/zope.testrunner/issues/125>`_).

- Add support for Python 3.10.


5.3.0 (2021-03-17)
==================

- Add support for Python 3.9.

- Fix `package init file missing` warning
  (`#112 <https://github.com/zopefoundation/zope.testrunner/pull/112>`_).

- Make standard streams provide a `buffer` attribute on Python 3 when using
  `--buffer` or testing under subunit.


5.2 (2020-06-29)
================

- Add support for Python 3.8.

- When a layer is run in a subprocess, read its stderr in a thread to avoid
  a deadlock if its stderr output (containing failing and erroring test IDs)
  overflows the capacity of a pipe (`#105
  <https://github.com/zopefoundation/zope.testrunner/issues/105>`_).


5.1 (2019-10-19)
================

- Recover more gracefully when layer setUp or tearDown fails, producing
  useful subunit output.

- Prevent a spurious warning from the ``--require-unique`` option if the
  ``--module`` option was not used.

- Add optional buffering of standard output and standard error during tests,
  requested via the ``--buffer`` option or enabled by default for subunit.

- Fix incorrect failure counts in per-layer summary output, broken in 4.0.1.


5.0 (2019-03-19)
================

- Fix test failures and deprecation warnings occurring when using Python 3.8a1.
  (`#89 <https://github.com/zopefoundation/zope.testrunner/pull/89>`_)

- Drop support for Python 3.4.


4.9.2 (2018-11-24)
==================

- Fix ``TypeError: a bytes-like object is required, not 'str'``
  running tests in parallel on Python 3. See `issue 80
  <https://github.com/zopefoundation/zope.testrunner/issues/80>`_.


4.9.1 (2018-11-21)
==================

- Fix AssertionError in _DummyThread.isAlive on Python 3 (`#81
  <https://github.com/zopefoundation/zope.testrunner/issues/81>`_).


4.9 (2018-10-05)
================

- Drop support for Python 3.3.

- Add support for Python 3.7.

- Enable test coverage reporting on coveralls.io and in tox.ini.

- Host documentation at https://zopetestrunner.readthedocs.io

- Remove untested support for the ``--pychecker`` option. See
  `issue 63 <https://github.com/zopefoundation/zope.testrunner/issues/63>`_.

- Update the command line interface to use ``argparse`` instead of
  ``optparse``. See `issue 61
  <https://github.com/zopefoundation/zope.testrunner/issues/61>`_.

- Use ipdb instead of pdb for post-mortem debugging if available
  (`#10 <https://github.com/zopefoundation/zope.testrunner/issues/10>`_).

- Add a --require-unique option to check for duplicate test IDs. See
  `LP #682771
  <https://bugs.launchpad.net/launchpad/+bug/682771>`_.

- Reintroduce optional support for ``subunit``, now with support for both
  version 1 and version 2 of its protocol.

- Handle string in exception values when formatting chained exceptions.
  (`#74 <https://github.com/zopefoundation/zope.testrunner/pull/74>`_)


4.8.1 (2017-11-12)
==================

- Enable ``DeprecationWarning`` earlier, when discovering test
  modules. This lets warnings that are raised on import (such as those
  produced by ``zope.deprecation.moved``) be reported. See `issue 57
  <https://github.com/zopefoundation/zope.testrunner/issues/57>`_.


4.8.0 (2017-11-10)
==================

- Automatically enable ``DeprecationWarning`` when running tests. This
  is recommended by the Python core developers and matches the
  behaviour of the ``unittest`` module. This can be overridden with
  Python command-line options (``-W``) or environment variables
  (``PYTHONWARNINGS``). See `issue 54
  <https://github.com/zopefoundation/zope.testrunner/issues/54>`_.

4.7.0 (2017-05-30)
==================

- Drop all support for ``subunit``.


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
