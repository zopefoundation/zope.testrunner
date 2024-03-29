Test Progress
=============

If the --progress (-p) option is used, progress information is printed and
a carriage return (rather than a new-line) is printed between
detail lines.  Let's look at the effect of --progress (-p) at different
levels of verbosity.

    >>> import os.path, sys
    >>> directory_with_tests = os.path.join(this_directory, 'testrunner-ex')
    >>> defaults = [
    ...     '--path', directory_with_tests,
    ...     '--tests-pattern', '^sampletestsf?$',
    ...     ]

    >>> sys.argv = 'test --layer 122 -p'.split()
    >>> from zope import testrunner
    >>> testrunner.run_internal(defaults)
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in N.NNN seconds.
      Set up samplelayers.Layer12 in N.NNN seconds.
      Set up samplelayers.Layer122 in N.NNN seconds.
      Running:
        1/26 (3.8%)##r##
                   ##r##
        2/26 (7.7%)##r##
                   ##r##
        3/26 (11.5%)##r##
                    ##r##
        4/26 (15.4%)##r##
                    ##r##
        5/26 (19.2%)##r##
                    ##r##
        6/26 (23.1%)##r##
                    ##r##
        7/26 (26.9%)##r##
                    ##r##
        8/26 (30.8%)##r##
                    ##r##
        9/26 (34.6%)##r##
                    ##r##
        10/26 (38.5%)##r##
                     ##r##
        11/26 (42.3%)##r##
                     ##r##
        12/26 (46.2%)##r##
                     ##r##
        13/26 (50.0%)##r##
                     ##r##
        14/26 (53.8%)##r##
                     ##r##
        15/26 (57.7%)##r##
                     ##r##
        16/26 (61.5%)##r##
                     ##r##
        17/26 (65.4%)##r##
                     ##r##
        18/26 (69.2%)##r##
                     ##r##
        19/26 (73.1%)##r##
                     ##r##
        20/26 (76.9%)##r##
                     ##r##
        21/26 (80.8%)##r##
                     ##r##
        22/26 (84.6%)##r##
                     ##r##
        23/26 (88.5%)##r##
                     ##r##
        24/26 (92.3%)##r##
                     ##r##
        25/26 (96.2%)##r##
                     ##r##
        26/26 (100.0%)##r##
                      ##r##
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in N.NNN seconds.
      Tear down samplelayers.Layer12 in N.NNN seconds.
      Tear down samplelayers.Layer1 in N.NNN seconds.
    False


(Note that, in the examples above and below, we show "##r##" followed by
new lines where carriage returns would appear in actual output.)

Using a single level of verbosity causes test descriptions to be
output, but only if they fit in the terminal width.  The default
width, when the terminal width can't be determined, is 80:

    >>> sys.argv = 'test --layer 122 -pv'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in N.NNN seconds.
      Set up samplelayers.Layer12 in N.NNN seconds.
      Set up samplelayers.Layer122 in N.NNN seconds.
      Running:
        1/26 (3.8%) test_x1 (sample1.sampletests.test122.TestA...)##r##
                                                               ##r##
        2/26 (7.7%) test_y0 (sample1.sampletests.test122.TestA...)##r##
                                                               ##r##
        3/26 (11.5%) test_z0 (sample1.sampletests.test122.TestA...)##r##
                                                                ##r##
        4/26 (15.4%) test_x0 (sample1.sampletests.test122.TestB...)##r##
                                                                ##r##
        5/26 (19.2%) test_y1 (sample1.sampletests.test122.TestB...)##r##
                                                                ##r##
        6/26 (23.1%) test_z0 (sample1.sampletests.test122.TestB...)##r##
                                                                ##r##
        7/26 (26.9%) test_1 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                     ##r##
        8/26 (30.8%) test_2 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                     ##r##
        9/26 (34.6%) test_3 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                     ##r##
        10/26 (38.5%) test_x0 (sample1.sampletests.test122)##r##
                                                           ##r##
        11/26 (42.3%) test_y0 (sample1.sampletests.test122)##r##
                                                           ##r##
        12/26 (46.2%) test_z1 (sample1.sampletests.test122)##r##
                                                           ##r##
     testrunner-ex/sample1/sampletests/../../sampletestsl.rst##r##
                                                                                   ##r##
        14/26 (53.8%) test_x1 (sampletests.test122.TestA...)##r##
                                                         ##r##
        15/26 (57.7%) test_y0 (sampletests.test122.TestA...)##r##
                                                         ##r##
        16/26 (61.5%) test_z0 (sampletests.test122.TestA...)##r##
                                                         ##r##
        17/26 (65.4%) test_x0 (sampletests.test122.TestB...)##r##
                                                         ##r##
        18/26 (69.2%) test_y1 (sampletests.test122.TestB...)##r##
                                                         ##r##
        19/26 (73.1%) test_z0 (sampletests.test122.TestB...)##r##
                                                         ##r##
        20/26 (76.9%) test_1 (sampletests.test122.TestNotMuch...)##r##
                                                              ##r##
        21/26 (80.8%) test_2 (sampletests.test122.TestNotMuch...)##r##
                                                              ##r##
        22/26 (84.6%) test_3 (sampletests.test122.TestNotMuch...)##r##
                                                              ##r##
        23/26 (88.5%) test_x0 (sampletests.test122)##r##
                                                   ##r##
        24/26 (92.3%) test_y0 (sampletests.test122)##r##
                                                   ##r##
        25/26 (96.2%) test_z1 (sampletests.test122)##r##
                                                   ##r##
     testrunner-ex/sampletests/../sampletestsl.rst##r##
                                                                                   ##r##
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in N.NNN seconds.
      Tear down samplelayers.Layer12 in N.NNN seconds.
      Tear down samplelayers.Layer1 in N.NNN seconds.
    False


The terminal width is determined using the curses module.  To see
that, we'll provide a fake curses module:

    >>> class FakeCurses:
    ...     class error(Exception):
    ...         pass
    ...     def setupterm(self):
    ...         pass
    ...     def tigetnum(self, ignored):
    ...         return 60
    >>> old_curses = sys.modules.get('curses')
    >>> sys.modules['curses'] = FakeCurses()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in N.NNN seconds.
      Set up samplelayers.Layer12 in N.NNN seconds.
      Set up samplelayers.Layer122 in N.NNN seconds.
      Running:
        1/26 (3.8%) test_x1 (...pletests.test122.TestA...)##r##
                                                               ##r##
        2/26 (7.7%) test_y0 (...pletests.test122.TestA...)##r##
                                                               ##r##
        3/26 (11.5%) test_z0 (...letests.test122.TestA...)##r##
                                                               ##r##
        4/26 (15.4%) test_x0 (...letests.test122.TestB...)##r##
                                                               ##r##
        5/26 (19.2%) test_y1 (...letests.test122.TestB...)##r##
                                                               ##r##
        6/26 (23.1%) test_z0 (...letests.test122.TestB...)##r##
                                                               ##r##
        7/26 (26.9%) test_1 (...sts.test122.TestNotMuch...)##r##
                                                               ##r##
        8/26 (30.8%) test_2 (...sts.test122.TestNotMuch...)##r##
                                                               ##r##
        9/26 (34.6%) test_3 (...sts.test122.TestNotMuch...)##r##
                                                               ##r##
        10/26 (38.5%) test_x0 (sample1.sampletests.test122)##r##
                                                           ##r##
        11/26 (42.3%) test_y0 (sample1.sampletests.test122)##r##
                                                           ##r##
        12/26 (46.2%) test_z1 (sample1.sampletests.test122)##r##
                                                           ##r##
        13/26 (50.0%) ... e1/sampletests/../../sampletestsl.rst##r##
                                                               ##r##
        14/26 (53.8%) test_x1 (...etests.test122.TestA...)##r##
                                                         ##r##
        15/26 (57.7%) test_y0 (...etests.test122.TestA...)##r##
                                                         ##r##
        16/26 (61.5%) test_z0 (...etests.test122.TestA...)##r##
                                                         ##r##
        17/26 (65.4%) test_x0 (...etests.test122.TestB...)##r##
                                                         ##r##
        18/26 (69.2%) test_y1 (...etests.test122.TestB...)##r##
                                                         ##r##
        19/26 (73.1%) test_z0 (...etests.test122.TestB...)##r##
                                                         ##r##
        20/26 (76.9%) test_1 (...ts.test122.TestNotMuch...)##r##
                                                              ##r##
        21/26 (80.8%) test_2 (...ts.test122.TestNotMuch...)##r##
                                                              ##r##
        22/26 (84.6%) test_3 (...ts.test122.TestNotMuch...)##r##
                                                              ##r##
        23/26 (88.5%) test_x0 (sampletests.test122)##r##
                                                   ##r##
        24/26 (92.3%) test_y0 (sampletests.test122)##r##
                                                   ##r##
        25/26 (96.2%) test_z1 (sampletests.test122)##r##
                                                   ##r##
        26/26 (100.0%) ... r-ex/sampletests/../sampletestsl.rst##r##
                                                               ##r##
      Ran 26 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in N.NNN seconds.
      Tear down samplelayers.Layer12 in N.NNN seconds.
      Tear down samplelayers.Layer1 in N.NNN seconds.
    False

    >>> sys.modules['curses'] = old_curses

If a second or third level of verbosity are added, we get additional
information.

    >>> sys.argv = 'test --layer 122 -pvv -t !rst'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer12 in 0.000 seconds.
      Set up samplelayers.Layer122 in 0.000 seconds.
      Running:
        1/24 (4.2%) test_x1 (sample1.sampletests.test122.TestA...)##r##
                                                              ##r##
        2/24 (8.3%) test_y0 (sample1.sampletests.test122.TestA...)##r##
                                                              ##r##
        3/24 (12.5%) test_z0 (sample1.sampletests.test122.TestA...)##r##
                                                               ##r##
        4/24 (16.7%) test_x0 (sample1.sampletests.test122.TestB...)##r##
                                                               ##r##
        5/24 (20.8%) test_y1 (sample1.sampletests.test122.TestB...)##r##
                                                               ##r##
        6/24 (25.0%) test_z0 (sample1.sampletests.test122.TestB...)##r##
                                                               ##r##
        7/24 (29.2%) test_1 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                    ##r##
        8/24 (33.3%) test_2 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                    ##r##
        9/24 (37.5%) test_3 (sample1.sampletests.test122.TestNotMuch...)##r##
                                                                    ##r##
        10/24 (41.7%) test_x0 (sample1.sampletests.test122)##r##
                                                          ##r##
        11/24 (45.8%) test_y0 (sample1.sampletests.test122)##r##
                                                          ##r##
        12/24 (50.0%) test_z1 (sample1.sampletests.test122)##r##
                                                          ##r##
        13/24 (54.2%) test_x1 (sampletests.test122.TestA...)##r##
                                                        ##r##
        14/24 (58.3%) test_y0 (sampletests.test122.TestA...)##r##
                                                        ##r##
        15/24 (62.5%) test_z0 (sampletests.test122.TestA...)##r##
                                                        ##r##
        16/24 (66.7%) test_x0 (sampletests.test122.TestB...)##r##
                                                        ##r##
        17/24 (70.8%) test_y1 (sampletests.test122.TestB...)##r##
                                                        ##r##
        18/24 (75.0%) test_z0 (sampletests.test122.TestB...)##r##
                                                        ##r##
        19/24 (79.2%) test_1 (sampletests.test122.TestNotMuch...)##r##
                                                             ##r##
        20/24 (83.3%) test_2 (sampletests.test122.TestNotMuch...)##r##
                                                             ##r##
        21/24 (87.5%) test_3 (sampletests.test122.TestNotMuch...)##r##
                                                             ##r##
        22/24 (91.7%) test_x0 (sampletests.test122)##r##
                                                  ##r##
        23/24 (95.8%) test_y0 (sampletests.test122)##r##
                                                  ##r##
        24/24 (100.0%) test_z1 (sampletests.test122)##r##
                                                   ##r##
      Ran 24 tests with 0 failures, 0 errors and 0 skipped in 0.006 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in 0.000 seconds.
      Tear down samplelayers.Layer12 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.
    False

Note that, in this example, we used a test-selection pattern starting
with '!' to exclude tests containing the string "rst".

    >>> sys.argv = 'test --layer 122 -pvvv -t!(rst|NotMuch)'.split()
    >>> testrunner.run_internal(defaults)
    Running tests at level 1
    Running samplelayers.Layer122 tests:
      Set up samplelayers.Layer1 in 0.000 seconds.
      Set up samplelayers.Layer12 in 0.000 seconds.
      Set up samplelayers.Layer122 in 0.000 seconds.
      Running:
        1/18 (5.6%) test_x1 (sample1.sampletests.test122.TestA...) (0.000 s)##r##
                                                                          ##r##
        2/18 (11.1%) test_y0 (sample1.sampletests.test122.TestA...) (0.000 s)##r##
                                                                           ##r##
        3/18 (16.7%) test_z0 (sample1.sampletests.test122.TestA...) (0.000 s)##r##
                                                                           ##r##
        4/18 (22.2%) test_x0 (sample1.sampletests.test122.TestB...) (0.000 s)##r##
                                                                           ##r##
        5/18 (27.8%) test_y1 (sample1.sampletests.test122.TestB...) (0.000 s)##r##
                                                                           ##r##
        6/18 (33.3%) test_z0 (sample1.sampletests.test122.TestB...) (0.000 s)##r##
                                                                           ##r##
        7/18 (38.9%) test_x0 (sample1.sampletests.test122) (0.001 s)##r##
                                                                     ##r##
        8/18 (44.4%) test_y0 (sample1.sampletests.test122) (0.001 s)##r##
                                                                     ##r##
        9/18 (50.0%) test_z1 (sample1.sampletests.test122) (0.001 s)##r##
                                                                     ##r##
        10/18 (55.6%) test_x1 (sampletests.test122.TestA...) (0.000 s)##r##
                                                                    ##r##
        11/18 (61.1%) test_y0 (sampletests.test122.TestA...) (0.000 s)##r##
                                                                    ##r##
        12/18 (66.7%) test_z0 (sampletests.test122.TestA...) (0.000 s)##r##
                                                                    ##r##
        13/18 (72.2%) test_x0 (sampletests.test122.TestB...) (0.000 s)##r##
                                                                    ##r##
        14/18 (77.8%) test_y1 (sampletests.test122.TestB...) (0.000 s)##r##
                                                                    ##r##
        15/18 (83.3%) test_z0 (sampletests.test122.TestB...) (0.000 s)##r##
                                                                    ##r##
        16/18 (88.9%) test_x0 (sampletests.test122) (0.001 s)##r##
                                                              ##r##
        17/18 (94.4%) test_y0 (sampletests.test122) (0.001 s)##r##
                                                              ##r##
        18/18 (100.0%) test_z1 (sampletests.test122) (0.001 s)##r##
                                                               ##r##
      Ran 18 tests with 0 failures, 0 errors and 0 skipped in 0.006 seconds.
    Tearing down left over layers:
      Tear down samplelayers.Layer122 in 0.000 seconds.
      Tear down samplelayers.Layer12 in 0.000 seconds.
      Tear down samplelayers.Layer1 in 0.000 seconds.
    False

In this example, we also excluded tests with "NotMuch" in their names.

Unfortunately, the time data above doesn't buy us much because, in
practice, the line is cleared before there is time to see the
times. :/


Autodetecting progress
----------------------

The --auto-progress option will determine if stdout is a terminal, and only enable
progress output if so.

Let's pretend we have a terminal

    >>> class Terminal(object):
    ...     def __init__(self, stream):
    ...         self._stream = stream
    ...     def __getattr__(self, attr):
    ...         return getattr(self._stream, attr)
    ...     def isatty(self):
    ...         return True
    >>> real_stdout = sys.stdout
    >>> sys.stdout = Terminal(sys.stdout)

    >>> sys.argv = 'test -u -t test_one.TestNotMuch --auto-progress'.split()
    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Running:
        1/6 (16.7%)##r##
                   ##r##
        2/6 (33.3%)##r##
                   ##r##
        3/6 (50.0%)##r##
                   ##r##
        4/6 (66.7%)##r##
                   ##r##
        5/6 (83.3%)##r##
                   ##r##
        6/6 (100.0%)##r##
                    ##r##
      Ran 6 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Let's stop pretending

    >>> sys.stdout = real_stdout

    >>> sys.argv = 'test -u -t test_one.TestNotMuch --auto-progress'.split()
    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 6 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False


Disabling progress indication
-----------------------------

If -p or --progress have been previously provided on the command line (perhaps by a
wrapper script) but you do not desire progress indication, you can switch it off with
--no-progress:

    >>> sys.argv = 'test -u -t test_one.TestNotMuch -p --no-progress'.split()
    >>> testrunner.run_internal(defaults)
    Running zope.testrunner.layer.UnitTests tests:
      Set up zope.testrunner.layer.UnitTests in N.NNN seconds.
      Ran 6 tests with 0 failures, 0 errors and 0 skipped in N.NNN seconds.
    Tearing down left over layers:
      Tear down zope.testrunner.layer.UnitTests in N.NNN seconds.
    False
