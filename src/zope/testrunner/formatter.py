##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Output formatting.
"""
import doctest
import io
import os
import re
import socket
import sys
import tempfile
import traceback
from collections.abc import MutableMapping
from contextlib import contextmanager
from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from xml.etree import ElementTree

from zope.testrunner.exceptions import DocTestFailureException
from zope.testrunner.find import StartUpFailure


try:
    import manuel.testing
    HAVE_MANUEL = True
except ImportError:
    HAVE_MANUEL = False


doctest_template = """
File "%s", line %s, in %s

%s
Want:
%s
Got:
%s
"""


class OutputFormatter:
    """Test runner output formatter."""

    # Implementation note: be careful about printing stuff to sys.stderr.
    # It is used for interprocess communication between the parent and the
    # child test runner, when you run some test layers in a subprocess.
    # resume_layer() reasigns sys.stderr for this reason, but be careful
    # and don't store the original one in __init__ or something.

    max_width = 80

    def __init__(self, options):
        self.options = options
        self.last_width = 0
        self.compute_max_width()

    progress = property(lambda self: self.options.progress)
    verbose = property(lambda self: self.options.verbose)
    in_subprocess = property(
        lambda self: (
            self.options.resume_layer is not None and
            self.options.processes > 1))

    def compute_max_width(self):
        """Try to determine the terminal width."""
        # Note that doing this every time is more test friendly.
        self.max_width = tigetnum('cols', self.max_width)

    def getShortDescription(self, test, room):
        """Return a description of a test that fits in ``room`` characters."""
        room -= 1
        s = str(test)
        if len(s) > room:
            pos = s.find(" (")
            if pos >= 0:
                w = room - (pos + 5)
                if w < 1:
                    # first portion (test method name) is too long
                    s = s[:room - 3] + "..."
                else:
                    pre = s[:pos + 2]
                    post = s[-w:]
                    s = f"{pre}...{post}"
            else:
                w = room - 4
                s = '... ' + s[-w:]

        return ' ' + s[:room]

    def info(self, message):
        """Print an informative message."""
        print(message)

    def info_suboptimal(self, message):
        """Print an informative message about losing some of the features.

        For example, when you run some tests in a subprocess, you lose the
        ability to use the debugger.
        """
        print(message)

    def error(self, message):
        """Report an error."""
        print(message)

    def error_with_banner(self, message):
        """Report an error with a big ASCII banner."""
        print()
        print('*' * 70)
        self.error(message)
        print('*' * 70)
        print()

    def profiler_stats(self, stats):
        """Report profiler stats."""
        stats.print_stats(50)

    def import_errors(self, import_errors):
        """Report test-module import errors (if any)."""
        if import_errors:
            print("Test-module import failures:")
            for error in import_errors:
                self.print_traceback("Module: %s\n" % error.module,
                                     error.exc_info),
            print()

    def tests_with_errors(self, errors):
        """Report names of tests with errors (if any)."""
        if errors:
            print()
            print("Tests with errors:")
            for test, exc_info in errors:
                print("  ", test)

    def tests_with_failures(self, failures):
        """Report names of tests with failures (if any)."""
        if failures:
            print()
            print("Tests with failures:")
            for test, exc_info in failures:
                print("  ", test)

    def modules_with_import_problems(self, import_errors):
        """Report names of modules with import problems (if any)."""
        if import_errors:
            print()
            print("Test-modules with import problems:")
            for test in import_errors:
                print("  " + test.module)

    def format_seconds(self, n_seconds):
        """Format a time in seconds."""
        if n_seconds >= 60:
            n_minutes, n_seconds = divmod(n_seconds, 60)
            return "%d minutes %.3f seconds" % (n_minutes, n_seconds)
        else:
            return "%.3f seconds" % n_seconds

    def format_seconds_short(self, n_seconds):
        """Format a time in seconds (short version)."""
        return "%.3f s" % n_seconds

    def summary(self, n_tests, n_failures, n_errors, n_seconds,
                n_skipped=0):
        """Summarize the results of a single test layer."""
        print("  Ran %s tests with %s failures, %s errors and "
              "%s skipped in %s."
              % (n_tests, n_failures, n_errors, n_skipped,
                  self.format_seconds(n_seconds)))

    def totals(self, n_tests, n_failures, n_errors, n_seconds,
               n_skipped=0):
        """Summarize the results of all layers."""
        print("Total: %s tests, %s failures, %s errors and %s skipped in %s."
              % (n_tests, n_failures, n_errors, n_skipped,
                 self.format_seconds(n_seconds)))

    def list_of_tests(self, tests, layer_name):
        """Report a list of test names."""
        print("Listing %s tests:" % layer_name)
        for test in tests:
            print(' ', test)

    def garbage(self, garbage):
        """Report garbage generated by tests."""
        if garbage:
            print("Tests generated new (%d) garbage:" % len(garbage))
            print(garbage)

    def test_garbage(self, test, garbage):
        """Report garbage generated by a test."""
        if garbage:
            print("The following test left garbage:")
            print(test)
            print(garbage)

    def test_threads(self, test, new_threads):
        """Report threads left behind by a test."""
        if new_threads:
            print("The following test left new threads behind:")
            print(test)
            print("New thread(s):", new_threads)

    def test_cycles(self, test, cycles):
        """Report cyclic garbage left behind by a test."""
        if cycles:
            print("The following test left cyclic garbage behind:")
            print(test)
            for i, cy in enumerate(cycles):
                print("Cycle", i + 1)
                for oi in cy:
                    print(" * ", "\n   ".join(oi))

    def refcounts(self, rc, prev):
        """Report a change in reference counts."""
        print("  sys refcount=%-8d change=%-6d" % (rc, rc - prev))

    def detailed_refcounts(self, track, rc, prev):
        """Report a change in reference counts, with extra detail."""
        print("  sum detail refcount=%-8d"
              " sys refcount=%-8d"
              " change=%-6d"
              % (track.n, rc, rc - prev))
        track.output()

    def start_set_up(self, layer_name):
        """Report that we're setting up a layer.

        The next output operation should be stop_set_up().
        """
        print("  Set up %s" % layer_name, end=' ')
        sys.stdout.flush()

    def stop_set_up(self, seconds):
        """Report that we've set up a layer.

        Should be called right after start_set_up().
        """
        print("in %s." % self.format_seconds(seconds))

    def start_tear_down(self, layer_name):
        """Report that we're tearing down a layer.

        The next output operation should be stop_tear_down() or
        tear_down_not_supported().
        """
        print("  Tear down %s" % layer_name, end=' ')
        sys.stdout.flush()

    def stop_tear_down(self, seconds):
        """Report that we've tore down a layer.

        Should be called right after start_tear_down().
        """
        print("in %s." % self.format_seconds(seconds))

    def tear_down_not_supported(self):
        """Report that we could not tear down a layer.

        Should be called right after start_tear_down().
        """
        print("... not supported")

    def start_test(self, test, tests_run, total_tests):
        """Report that we're about to run a test.

        The next output operation should be test_success(), test_error(), or
        test_failure().
        """
        self.test_width = 0
        if self.progress:
            if self.last_width:
                sys.stdout.write('\r' + (' ' * self.last_width) + '\r')

            s = "    %d/%d (%.1f%%)" % (tests_run, total_tests,
                                        tests_run * 100.0 / total_tests)
            sys.stdout.write(s)
            self.test_width += len(s)
            if self.verbose == 1:
                room = self.max_width - self.test_width - 1
                s = self.getShortDescription(test, room)
                sys.stdout.write(s)
                self.test_width += len(s)

        elif self.verbose == 1:
            sys.stdout.write('.' * test.countTestCases())

        elif self.in_subprocess:
            sys.stdout.write('.' * test.countTestCases())
            # Give the parent process a new line so it sees the progress
            # in a timely manner.
            sys.stdout.write('\n')

        if self.verbose > 1:
            s = str(test)
            sys.stdout.write(' ')
            sys.stdout.write(s)
            self.test_width += len(s) + 1

        sys.stdout.flush()

    def test_success(self, test, seconds):
        """Report that a test was successful.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        if self.verbose > 2:
            s = " (%s)" % self.format_seconds_short(seconds)
            sys.stdout.write(s)
            self.test_width += len(s) + 1

    def test_skipped(self, test, reason):
        """Report that a test was skipped.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        if self.verbose > 2:
            s = " (skipped: %s)" % reason
        elif self.verbose > 1:
            s = " (skipped)"
        else:
            return
        sys.stdout.write(s)
        self.test_width += len(s) + 1

    def test_error(self, test, seconds, exc_info, stdout=None, stderr=None):
        """Report that an error occurred while running a test.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        if self.verbose > 2:
            print(" (%s)" % self.format_seconds_short(seconds))
        print()
        self.print_traceback("Error in test %s" % test, exc_info)
        self.print_std_streams(stdout, stderr)
        self.test_width = self.last_width = 0

    def test_failure(self, test, seconds, exc_info, stdout=None, stderr=None):
        """Report that a test failed.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        if self.verbose > 2:
            print(" (%s)" % self.format_seconds_short(seconds))
        print()
        self.print_traceback("Failure in test %s" % test, exc_info)
        self.print_std_streams(stdout, stderr)
        self.test_width = self.last_width = 0

    def print_traceback(self, msg, exc_info):
        """Report an error with a traceback."""
        print()
        print(msg)
        print(self.format_traceback(exc_info))

    def print_std_streams(self, stdout, stderr):
        """Emit contents of buffered standard streams."""
        if stdout:
            sys.stdout.write("Stdout:\n")
            sys.stdout.write(stdout)
            if not stdout.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.write("\n")
        if stderr:
            sys.stderr.write("Stderr:\n")
            sys.stderr.write(stderr)
            if not stderr.endswith("\n"):
                sys.stderr.write("\n")
            sys.stderr.write("\n")

    def format_traceback(self, exc_info):
        """Format the traceback."""
        v = exc_info[1]
        if isinstance(v, DocTestFailureException):
            tb = v.args[0]
        elif isinstance(v, doctest.DocTestFailure):
            tb = doctest_template % (
                v.test.filename,
                v.test.lineno + v.example.lineno + 1,
                v.test.name,
                v.example.source,
                v.example.want,
                v.got,
            )
        else:
            tb = "".join(traceback.format_exception(*exc_info))
        return tb

    def stop_test(self, test, gccount):
        """Clean up the output state after a test."""
        if gccount and self.verbose:
            s = "!" if self.verbose == 1 else " [%d]" % gccount
            self.test_width += len(s)
            print(s, end="")
        if self.progress:
            self.last_width = self.test_width
        elif self.verbose > 1:
            print()
        sys.stdout.flush()

    def stop_tests(self):
        """Clean up the output state after a collection of tests."""
        if self.progress and self.last_width:
            sys.stdout.write('\r' + (' ' * self.last_width) + '\r')
        if self.verbose == 1 or self.progress:
            print()


def tigetnum(attr, default=None):
    """Return a value from the terminfo database.

    Terminfo is used on Unix-like systems to report various terminal attributes
    (such as width, height or the number of supported colors).

    Returns ``default`` when the ``curses`` module is not available, or when
    sys.stdout is not a terminal.
    """
    try:
        import curses
    except ImportError:
        # avoid reimporting a broken module
        sys.modules['curses'] = None
    else:
        # If sys.stdout is not a real file object (e.g. in unit tests that
        # use various wrappers), you get an error, different depending on
        # Python version:
        expected_exceptions = (
            curses.error, TypeError, AttributeError, io.UnsupportedOperation)
        try:
            curses.setupterm()
        except expected_exceptions:
            # You get curses.error when $TERM is set to an unknown name
            pass
        else:
            try:
                return curses.tigetnum(attr)
            except expected_exceptions:
                # You get TypeError on PyPy3 due to a bug:
                # https://bitbucket.org/pypy/pypy/issue/2016/pypy3-cursestigetnum-raises-ctype
                pass
    return default


def terminal_has_colors():
    """Determine whether the terminal supports colors.

    Some terminals (e.g. the emacs built-in one) don't.
    """
    return tigetnum('colors', -1) >= 8


class ColorfulOutputFormatter(OutputFormatter):
    """Output formatter that uses ANSI color codes.

    Like syntax highlighting in your text editor, colorizing
    test failures helps the developer.
    """

    # These colors are carefully chosen to have enough contrast
    # on terminals with both black and white background.
    colorscheme = {'normal': 'normal',
                   'default': 'default',
                   'info': 'normal',
                   'suboptimal-behaviour': 'magenta',
                   'error': 'brightred',
                   'number': 'green',
                   'slow-test': 'brightmagenta',
                   'ok-number': 'green',
                   'error-number': 'brightred',
                   'filename': 'lightblue',
                   'lineno': 'lightred',
                   'testname': 'lightcyan',
                   'failed-example': 'cyan',
                   'expected-output': 'green',
                   'actual-output': 'red',
                   'character-diffs': 'magenta',
                   'diff-chunk': 'magenta',
                   'exception': 'red',
                   'skipped': 'brightyellow',
                   }

    # Map prefix character to color in diff output.  This handles ndiff and
    # udiff correctly, but not cdiff.  In cdiff we ought to highlight '!' as
    # expected-output until we see a '-', then highlight '!' as actual-output,
    # until we see a '*', then switch back to highlighting '!' as
    # expected-output.  Nevertheless, coloried cdiffs are reasonably readable,
    # so I'm not going to fix this.
    #   -- mgedmin
    diff_color = {'-': 'expected-output',
                  '+': 'actual-output',
                  '?': 'character-diffs',
                  '@': 'diff-chunk',
                  '*': 'diff-chunk',
                  '!': 'actual-output',
                  }

    prefixes = [('dark', '0;'),
                ('light', '1;'),
                ('bright', '1;'),
                ('bold', '1;'),
                ]

    colorcodes = {'default': 0, 'normal': 0,
                  'black': 30,
                  'red': 31,
                  'green': 32,
                  'brown': 33, 'yellow': 33,
                  'blue': 34,
                  'magenta': 35,
                  'cyan': 36,
                  'grey': 37, 'gray': 37, 'white': 37}

    slow_test_threshold = 10.0  # seconds

    def color_code(self, color):
        """Convert a color description (e.g. 'lightred') to a terminal code."""
        prefix_code = ''
        for prefix, code in self.prefixes:
            if color.startswith(prefix):
                color = color[len(prefix):]
                prefix_code = code
                break
        color_code = self.colorcodes[color]
        return f'\033[{prefix_code}{color_code}m'

    def color(self, what):
        """Pick a named color from the color scheme"""
        return self.color_code(self.colorscheme[what])

    def colorize(self, what, message, normal='normal'):
        """Wrap message in color."""
        return self.color(what) + message + self.color(normal)

    def error_count_color(self, n):
        """Choose a color for the number of errors."""
        if n:
            return self.color('error-number')
        else:
            return self.color('ok-number')

    def skip_count_color(self, n):
        """Choose a color for the number of skipped tests."""
        if n:
            return self.color('skipped')
        else:
            return self.color('ok-number')

    def test_skipped(self, test, reason):
        """Report that a test was skipped.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        if self.verbose > 2:
            s = " ({}skipped: {}{})".format(
                self.color('skipped'), reason, self.color('info'))
        elif self.verbose > 1:
            s = " ({}skipped{})".format(
                self.color('skipped'), self.color('info'))
        else:
            return
        sys.stdout.write(s)
        self.test_width += len(s) + 1

    def info(self, message):
        """Print an informative message."""
        print(self.colorize('info', message))

    def info_suboptimal(self, message):
        """Print an informative message about losing some of the features.

        For example, when you run some tests in a subprocess, you lose the
        ability to use the debugger.
        """
        print(self.colorize('suboptimal-behaviour', message))

    def error(self, message):
        """Report an error."""
        print(self.colorize('error', message))

    def error_with_banner(self, message):
        """Report an error with a big ASCII banner."""
        print()
        print(self.colorize('error', '*' * 70))
        self.error(message)
        print(self.colorize('error', '*' * 70))
        print()

    def tear_down_not_supported(self):
        """Report that we could not tear down a layer.

        Should be called right after start_tear_down().
        """
        print("...", self.colorize('suboptimal-behaviour', "not supported"))

    def format_seconds(self, n_seconds, normal='normal'):
        """Format a time in seconds."""
        if n_seconds >= 60:
            n_minutes, n_seconds = divmod(n_seconds, 60)
            return "{} minutes {} seconds".format(
                self.colorize('number', '%d' % n_minutes, normal),
                self.colorize('number', '%.3f' % n_seconds, normal))
        else:
            return "%s seconds" % (
                self.colorize('number', '%.3f' % n_seconds, normal))

    def format_seconds_short(self, n_seconds):
        """Format a time in seconds (short version)."""
        if n_seconds >= self.slow_test_threshold:
            color = 'slow-test'
        else:
            color = 'number'
        return self.colorize(color, "%.3f s" % n_seconds)

    def summary(self, n_tests, n_failures, n_errors, n_seconds,
                n_skipped=0):
        """Summarize the results."""
        sys.stdout.writelines([
            self.color('info'), '  Ran ',
            self.color('number'), str(n_tests),
            self.color('info'), ' tests with ',
            self.error_count_color(n_failures), str(n_failures),
            self.color('info'), ' failures, ',
            self.error_count_color(n_errors), str(n_errors),
            self.color('info'), ' errors, ',
            self.skip_count_color(n_skipped), str(n_skipped),
            self.color('info'), ' skipped in ',
            self.format_seconds(n_seconds, 'info'), '.',
            self.color('normal'), '\n',
        ])

    def totals(self, n_tests, n_failures, n_errors, n_seconds,
               n_skipped=0):
        """Report totals (number of tests, failures, and errors)."""
        sys.stdout.writelines([
            self.color('info'), 'Total: ',
            self.color('number'), str(n_tests),
            self.color('info'), ' tests, ',
            self.error_count_color(n_failures), str(n_failures),
            self.color('info'), ' failures, ',
            self.error_count_color(n_errors), str(n_errors),
            self.color('info'), ' errors, ',
            self.skip_count_color(n_skipped), str(n_skipped),
            self.color('info'), ' skipped in ',
            self.format_seconds(n_seconds, 'info'), '.',
            self.color('normal'), '\n'])

    def print_traceback(self, msg, exc_info):
        """Report an error with a traceback."""
        print()
        print(self.colorize('error', msg))
        v = exc_info[1]
        if isinstance(v, DocTestFailureException):
            self.print_doctest_failure(v.args[0])
        elif isinstance(v, doctest.DocTestFailure):
            # I don't think these are ever used... -- mgedmin
            tb = self.format_traceback(exc_info)
            print(tb)
        else:
            tb = self.format_traceback(exc_info)
            self.print_colorized_traceback(tb)

    def print_doctest_failure(self, formatted_failure):
        """Report a doctest failure.

        ``formatted_failure`` is a string -- that's what
        DocTestSuite/DocFileSuite gives us.
        """
        color_of_indented_text = 'normal'
        colorize_diff = False
        for line in formatted_failure.splitlines():
            if line.startswith('File '):
                m = re.match(r'File "(.*)", line (\d*), in (.*)$', line)
                if m:
                    filename, lineno, test = m.groups()
                    sys.stdout.writelines([
                        self.color('normal'), 'File "',
                        self.color('filename'), filename,
                        self.color('normal'), '", line ',
                        self.color('lineno'), lineno,
                        self.color('normal'), ', in ',
                        self.color('testname'), test,
                        self.color('normal'), '\n'])
                else:
                    print(line)
            elif line.startswith('    ') or line.strip() == '':
                if colorize_diff and len(line) > 4:
                    color = self.diff_color.get(
                        line[4], color_of_indented_text)
                    print(self.colorize(color, line))
                else:
                    if line.strip() != '':
                        print(self.colorize(color_of_indented_text, line))
                    else:
                        print(line)
            else:
                colorize_diff = False
                if line.startswith('Failed example'):
                    color_of_indented_text = 'failed-example'
                elif line.startswith('Expected:'):
                    color_of_indented_text = 'expected-output'
                elif line.startswith('Got:'):
                    color_of_indented_text = 'actual-output'
                elif line.startswith('Exception raised:'):
                    color_of_indented_text = 'exception'
                elif line.startswith('Differences '):
                    color_of_indented_text = 'normal'
                    colorize_diff = True
                else:
                    color_of_indented_text = 'normal'
                print(line)
        print()

    def print_colorized_traceback(self, formatted_traceback):
        """Report a test failure.

        ``formatted_traceback`` is a string.
        """
        for line in formatted_traceback.splitlines():
            if line.startswith('  File'):
                m = re.match(r'  File "(.*)", line (\d*), in (.*)$', line)
                if m:
                    filename, lineno, test = m.groups()
                    sys.stdout.writelines([
                        self.color('normal'), '  File "',
                        self.color('filename'), filename,
                        self.color('normal'), '", line ',
                        self.color('lineno'), lineno,
                        self.color('normal'), ', in ',
                        self.color('testname'), test,
                        self.color('normal'), '\n'])
                else:
                    print(line)
            elif line.startswith('    '):
                print(self.colorize('failed-example', line))
            elif line.startswith('Traceback (most recent call last)'):
                print(line)
            else:
                print(self.colorize('exception', line))
        print()


class FakeTest:
    """A fake test object that only has an id."""

    failureException = None

    def __init__(self, test_id):
        self._id = test_id

    def id(self):
        return self._id


# Conditional imports: we don't want zope.testrunner to have a hard
# dependency on subunit.
try:
    import subunit
    from iso8601 import UTC
    subunit.StreamResultToBytes
except (ImportError, AttributeError):
    subunit = None


# testtools is a hard dependency of subunit itself, but we guard it
# separately for richer error messages.
try:
    import testtools
    from testtools.content import Content
    from testtools.content import ContentType
    from testtools.content import content_from_file
    from testtools.content import text_content
    testtools.StreamToExtendedDecorator
except (ImportError, AttributeError):
    testtools = None


class _RunnableDecorator:
    """Permit controlling the runnable annotation on tests.

    This decorates a StreamResult, adding a setRunnable context manager to
    indicate whether a test is runnable.  (A context manager is unidiomatic
    here, but it's just about the simplest way to stuff the relevant state
    through the various layers of decorators involved without accidentally
    affecting later test results.)
    """

    def __init__(self, decorated):
        self.decorated = decorated
        self._runnable = True

    def __getattr__(self, name):
        return getattr(self.decorated, name)

    @contextmanager
    def setRunnable(self, runnable):
        orig_runnable = self._runnable
        try:
            self._runnable = runnable
            yield
        finally:
            self._runnable = orig_runnable

    def status(self, **kwargs):
        kwargs = dict(kwargs)
        kwargs['runnable'] = self._runnable
        self.decorated.status(**kwargs)


class _SortedDict(MutableMapping):
    """A dict that always returns items in sorted order.

    This differs from collections.OrderedDict in that it returns items in
    *sorted* order, not in insertion order.

    We use this as a workaround for the fact that
    testtools.ExtendedToStreamDecorator doesn't sort the details dict when
    encoding it, which makes it difficult to write stable doctests for
    subunit v2 output.
    """

    def __init__(self, items):
        self._dict = dict(items)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(sorted(self._dict))

    def __len__(self):
        return len(self._dict)


class SubunitOutputFormatter:
    """A subunit output formatter.

    This output formatter generates subunit-compatible output (see
    https://launchpad.net/subunit).  Subunit output is essentially a stream
    of results of unit tests.

    In this formatter, non-test events (such as layer set up) are encoded as
    specially-tagged tests.  In particular, for a layer 'foo', the fake
    tests related to layer setup and teardown are tagged with 'zope:layer'
    and are called 'foo:setUp' and 'foo:tearDown'.  Any tests within layer
    'foo' are tagged with 'zope:layer:foo'.

    Note that all tags specific to this formatter begin with 'zope:'.
    """

    # subunit output is designed for computers, so displaying a progress bar
    # isn't helpful.
    progress = False
    verbose = property(lambda self: self.options.verbose)

    TAG_INFO_SUBOPTIMAL = 'zope:info_suboptimal'
    TAG_ERROR_WITH_BANNER = 'zope:error_with_banner'
    TAG_LAYER = 'zope:layer'
    TAG_IMPORT_ERROR = 'zope:import_error'
    TAG_PROFILER_STATS = 'zope:profiler_stats'
    TAG_GARBAGE = 'zope:garbage'
    TAG_THREADS = 'zope:threads'
    TAG_REFCOUNTS = 'zope:refcounts'

    def __init__(self, options, stream=None):
        if subunit is None:
            raise Exception('Requires python-subunit 1.4.3 or better')
        if testtools is None:
            raise Exception('Requires testtools 0.9.30 or better')
        self.options = options

        if stream is None:
            stream = sys.stdout
        self._stream = stream
        self._subunit = self._subunit_factory(self._stream)

        # Used to track the last layer that was set up or torn down. Either
        # None or (layer_name, last_touched_time).
        self._last_layer = None
        self.UTC = UTC
        # Content types used in the output.
        self.TRACEBACK_CONTENT_TYPE = ContentType(
            'text', 'x-traceback', {'language': 'python', 'charset': 'utf8'})
        self.PROFILE_CONTENT_TYPE = ContentType(
            'application', 'x-binary-profile')
        self.PLAIN_TEXT = ContentType('text', 'plain', {'charset': 'utf8'})

    @classmethod
    def _subunit_factory(cls, stream):
        """Return a TestResult attached to the given stream."""
        return _RunnableDecorator(subunit.TestProtocolClient(stream))

    def _emit_timestamp(self, now=None):
        """Emit a timestamp to the subunit stream.

        If 'now' is not specified, use the current time on the system clock.
        """
        if now is None:
            now = datetime.now(self.UTC)
        self._subunit.time(now)
        return now

    def _emit_fake_test(self, message, tag, details=None):
        """Emit a successful fake test to the subunit stream.

        Use this to print tagged informative messages.
        """
        test = FakeTest(message)
        with self._subunit.setRunnable(False):
            self._subunit.startTest(test)
            self._subunit.tags([tag], [])
            self._subunit.addSuccess(test, details=details)
            self._subunit.stopTest(test)

    def _emit_error(self, error_id, tag, exc_info, runnable=False):
        """Emit an error to the subunit stream.

        Use this to pass on information about errors that occur outside of
        tests.
        """
        test = FakeTest(error_id)
        with self._subunit.setRunnable(runnable):
            self._subunit.startTest(test)
            self._subunit.tags([tag], [])
            self._subunit.addError(test, exc_info)
            self._subunit.stopTest(test)

    def _emit_failure(self, failure_id, tag, exc_info):
        """Emit an failure to the subunit stream.

        Use this to pass on information about failures that occur outside of
        tests.
        """
        test = FakeTest(failure_id)
        self._subunit.addFailure(test, exc_info)

    def _enter_layer(self, layer_name):
        """Tell subunit that we are entering a layer."""
        self._subunit.tags([f'zope:layer:{layer_name}'], [])

    def _exit_layer(self, layer_name):
        """Tell subunit that we are exiting a layer."""
        self._subunit.tags([], [f'zope:layer:{layer_name}'])

    def info(self, message):
        """Print an informative message."""
        # info() output is not relevant to actual test results.  It only
        # says things like "Running tests" or "Tearing down left over
        # layers", things that are communicated already by the subunit
        # stream.  Just suppress the info() output.
        pass

    def info_suboptimal(self, message):
        """Print an informative message about losing some of the features.

        For example, when you run some tests in a subprocess, you lose the
        ability to use the debugger.
        """
        # Used _only_ to indicate running in a subprocess.
        self._emit_fake_test(message.strip(), self.TAG_INFO_SUBOPTIMAL)

    def error(self, message):
        """Report an error."""
        # XXX: Mostly used for user errors, sometimes used for errors in the
        # test framework, sometimes used to record layer setUp failure (!!!).
        self._stream.write(f'{message}\n')

    def error_with_banner(self, message):
        """Report an error with a big ASCII banner."""
        # Either "Could not communicate with subprocess"
        # Or "Can't post-mortem debug when running a layer as a subprocess!"
        self._emit_fake_test(message, self.TAG_ERROR_WITH_BANNER)

    def profiler_stats(self, stats):
        """Report profiler stats."""
        fd, filename = tempfile.mkstemp(prefix='zope.testrunner-')
        os.close(fd)
        try:
            stats.dump_stats(filename)
            profile_content = content_from_file(
                filename, content_type=self.PROFILE_CONTENT_TYPE)
            details = {'profiler-stats': profile_content}
            # Name the test 'zope:profiler_stats' just like its tag.
            self._emit_fake_test(
                self.TAG_PROFILER_STATS, self.TAG_PROFILER_STATS, details)
        finally:
            os.unlink(filename)

    def import_errors(self, import_errors):
        """Report test-module import errors (if any)."""
        if import_errors:
            for error in import_errors:
                self._emit_error(
                    error.module, self.TAG_IMPORT_ERROR, error.exc_info,
                    runnable=True)

    def tests_with_errors(self, errors):
        """Report names of tests with errors (if any).

        Simply not supported by the subunit formatter. Fancy summary output
        doesn't make sense.
        """
        pass

    def tests_with_failures(self, failures):
        """Report names of tests with failures (if any).

        Simply not supported by the subunit formatter. Fancy summary output
        doesn't make sense.
        """
        pass

    def modules_with_import_problems(self, import_errors):
        """Report names of modules with import problems (if any)."""
        # This is simply a summary method, and subunit output doesn't
        # benefit from summaries.
        pass

    def summary(self, n_tests, n_failures, n_errors, n_seconds,
                n_skipped=0):
        """Summarize the results of a single test layer.

        Since subunit is a stream protocol format, it has no need for a
        summary. When the stream is finished other tools can generate a
        summary if so desired.
        """
        pass

    def totals(self, n_tests, n_failures, n_errors, n_seconds, n_skipped=0):
        """Summarize the results of all layers.

        Simply not supported by the subunit formatter. Fancy summary output
        doesn't make sense.
        """
        pass

    def _emit_exists(self, test):
        """Emit an indication that a test exists.

        With the v1 protocol, we just emit a fake success line.
        """
        self._subunit.addSuccess(test)

    def list_of_tests(self, tests, layer_name):
        """Report a list of test names."""
        self._enter_layer(layer_name)
        for test in tests:
            self._subunit.startTest(test)
            self._emit_exists(test)
            self._subunit.stopTest(test)
        self._exit_layer(layer_name)

    def garbage(self, garbage):
        """Report garbage generated by tests."""
        # XXX: Really, 'garbage', 'profiler_stats' and the 'refcounts' twins
        # ought to add extra details to a fake test that represents the
        # summary information for the whole suite. However, there's no event
        # on output formatters for "everything is really finished, honest". --
        # jml, 2010-02-14
        details = {'garbage': text_content(str(garbage))}
        self._emit_fake_test(self.TAG_GARBAGE, self.TAG_GARBAGE, details)

    def test_garbage(self, test, garbage):
        """Report garbage generated by a test.

        Encoded in the subunit stream as a test error.  Clients can filter
        out these tests based on the tag if they don't think garbage should
        fail the test run.
        """
        # XXX: Perhaps 'test_garbage' and 'test_threads' ought to be within
        # the output for the actual test, appended as details to whatever
        # result the test gets. Not an option with the present API, as there's
        # no event for "no more output for this test". -- jml, 2010-02-14
        self._subunit.startTest(test)
        self._subunit.tags([self.TAG_GARBAGE], [])
        self._subunit.addError(
            test, details={'garbage': text_content(str(garbage))})
        self._subunit.stopTest(test)

    def test_threads(self, test, new_threads):
        """Report threads left behind by a test.

        Encoded in the subunit stream as a test error.  Clients can filter
        out these tests based on the tag if they don't think left-over
        threads should fail the test run.
        """
        self._subunit.startTest(test)
        self._subunit.tags([self.TAG_THREADS], [])
        self._subunit.addError(
            test, details={'threads': text_content(str(new_threads))})
        self._subunit.stopTest(test)

    def test_cycles(self, test, cycles):
        """Report cycles left behind by a test."""
        pass  # not implemented

    def refcounts(self, rc, prev):
        """Report a change in reference counts."""
        details = _SortedDict({
            'sys-refcounts': text_content(str(rc)),
            'changes': text_content(str(rc - prev)),
        })
        # XXX: Emit the details dict as JSON?
        self._emit_fake_test(self.TAG_REFCOUNTS, self.TAG_REFCOUNTS, details)

    def detailed_refcounts(self, track, rc, prev):
        """Report a change in reference counts, with extra detail."""
        details = _SortedDict({
            'sys-refcounts': text_content(str(rc)),
            'changes': text_content(str(rc - prev)),
            'track': text_content(str(track.delta)),
        })
        self._emit_fake_test(self.TAG_REFCOUNTS, self.TAG_REFCOUNTS, details)

    def start_set_up(self, layer_name):
        """Report that we're setting up a layer.

        We do this by emitting a fake test of the form '$LAYER_NAME:setUp'
        and adding a tag of the form 'zope:layer:$LAYER_NAME' to the current
        tag context.

        The next output operation should be stop_set_up().
        """
        test = FakeTest(f'{layer_name}:setUp')
        now = self._emit_timestamp()
        with self._subunit.setRunnable(False):
            self._subunit.startTest(test)
            self._subunit.tags([self.TAG_LAYER], [])
        self._last_layer = (layer_name, now)

    def stop_set_up(self, seconds):
        """Report that we've set up a layer.

        Should be called right after start_set_up().
        """
        layer_name, start_time = self._last_layer
        self._last_layer = None
        test = FakeTest(f'{layer_name}:setUp')
        self._emit_timestamp(start_time + timedelta(seconds=seconds))
        with self._subunit.setRunnable(False):
            self._subunit.addSuccess(test)
            self._subunit.stopTest(test)
        self._enter_layer(layer_name)

    def layer_failure(self, failure_type, exc_info):
        layer_name, start_time = self._last_layer
        self._emit_failure(
            f'{layer_name}:{failure_type}', self.TAG_LAYER, exc_info)

    def start_tear_down(self, layer_name):
        """Report that we're tearing down a layer.

        We do this by emitting a fake test of the form
        '$LAYER_NAME:tearDown' and removing a tag of the form
        'layer:$LAYER_NAME' from the current tag context.

        The next output operation should be stop_tear_down() or
        tear_down_not_supported().
        """
        test = FakeTest(f'{layer_name}:tearDown')
        self._exit_layer(layer_name)
        now = self._emit_timestamp()
        with self._subunit.setRunnable(False):
            self._subunit.startTest(test)
            self._subunit.tags([self.TAG_LAYER], [])
        self._last_layer = (layer_name, now)

    def stop_tear_down(self, seconds):
        """Report that we've torn down a layer.

        Should be called right after start_tear_down().
        """
        layer_name, start_time = self._last_layer
        self._last_layer = None
        test = FakeTest(f'{layer_name}:tearDown')
        self._emit_timestamp(start_time + timedelta(seconds=seconds))
        with self._subunit.setRunnable(False):
            self._subunit.addSuccess(test)
            self._subunit.stopTest(test)

    def tear_down_not_supported(self):
        """Report that we could not tear down a layer.

        Should be called right after start_tear_down().
        """
        layer_name, start_time = self._last_layer
        self._last_layer = None
        test = FakeTest(f'{layer_name}:tearDown')
        self._emit_timestamp()
        with self._subunit.setRunnable(False):
            self._subunit.addSkip(test, 'tearDown not supported')
            self._subunit.stopTest(test)

    def start_test(self, test, tests_run, total_tests):
        """Report that we're about to run a test.

        The next output operation should be test_success(), test_error(), or
        test_failure().
        """
        self._emit_timestamp()
        self._subunit.startTest(test)

    def test_success(self, test, seconds):
        """Report that a test was successful.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        self._emit_timestamp()
        self._subunit.addSuccess(test)

    def test_skipped(self, test, reason):
        """Report that a test was skipped.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        self._subunit.addSkip(test, reason)

    def _exc_info_to_details(self, exc_info):
        """Translate 'exc_info' into a details dict usable with subunit."""
        # In an ideal world, we'd use the pre-bundled 'TracebackContent'
        # class from testtools.  However, 'OutputFormatter' contains special
        # logic to handle errors from doctests, so we have to use that and
        # manually create an object equivalent to an instance of
        # 'TracebackContent'.
        formatter = OutputFormatter(None)
        traceback = formatter.format_traceback(exc_info)

        # We have no idea if the traceback is a str object or a
        # bytestring with non-ASCII characters.  We had best be careful when
        # handling it.
        if isinstance(traceback, bytes):
            # Assume the traceback was UTF-8-encoded, but still be careful.
            str_tb = traceback.decode('utf-8', 'replace')
        else:
            str_tb = traceback

        return _SortedDict({
            'traceback': Content(
                self.TRACEBACK_CONTENT_TYPE,
                lambda: [str_tb.encode('utf8')]),
        })

    def _add_std_streams_to_details(self, details, stdout, stderr):
        """Add buffered standard stream contents to a subunit details dict."""
        if stdout:
            if isinstance(stdout, bytes):
                stdout = stdout.decode('utf-8', 'replace')
            details['test-stdout'] = Content(
                self.PLAIN_TEXT, lambda: [stdout.encode('utf-8')])
        if stderr:
            if isinstance(stderr, bytes):
                stderr = stderr.decode('utf-8', 'replace')
            details['test-stderr'] = Content(
                self.PLAIN_TEXT, lambda: [stderr.encode('utf-8')])

    def test_error(self, test, seconds, exc_info, stdout=None, stderr=None):
        """Report that an error occurred while running a test.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        self._emit_timestamp()
        details = self._exc_info_to_details(exc_info)
        self._add_std_streams_to_details(details, stdout, stderr)
        self._subunit.addError(test, details=details)

    def test_failure(self, test, seconds, exc_info, stdout=None, stderr=None):
        """Report that a test failed.

        Should be called right after start_test().

        The next output operation should be stop_test().
        """
        self._emit_timestamp()
        details = self._exc_info_to_details(exc_info)
        self._add_std_streams_to_details(details, stdout, stderr)
        self._subunit.addFailure(test, details=details)

    def stop_test(self, test, gccount):
        """Clean up the output state after a test."""
        self._subunit.stopTest(test)

    def stop_tests(self):
        """Clean up the output state after a collection of tests."""
        # subunit handles all of this itself.
        pass


class SubunitV2OutputFormatter(SubunitOutputFormatter):
    """A subunit v2 output formatter."""

    @classmethod
    def _subunit_factory(cls, stream):
        """Return a TestResult attached to the given stream."""
        stream_result = _RunnableDecorator(subunit.StreamResultToBytes(stream))
        result = testtools.ExtendedToStreamDecorator(stream_result)
        # Lift our decorating method up so that we can get at it easily.
        result.setRunnable = stream_result.setRunnable
        result.startTestRun()
        return result

    def error(self, message):
        """Report an error."""
        # XXX: Mostly used for user errors, sometimes used for errors in the
        # test framework, sometimes used to record layer setUp failure (!!!).
        self._subunit.status(
            file_name='error', file_bytes=str(message).encode('utf-8'),
            eof=True, mime_type=repr(self.PLAIN_TEXT))

    def _emit_exists(self, test):
        """Emit an indication that a test exists."""
        now = datetime.now(self.UTC)
        self._subunit.status(
            test_id=test.id(), test_status='exists',
            test_tags=self._subunit.current_tags, timestamp=now)


@dataclass
class TestSuiteInfo:

    testCases: list = field(default_factory=list)
    errors: int = 0
    failures: int = 0
    time: float = 0.0

    @property
    def tests(self):
        return len(self.testCases)

    @property
    def successes(self):
        return self.tests - self.errors - self.failures


@dataclass
class TestCaseInfo:

    test: object
    time: float
    testClassName: str
    testName: str
    failure: bool = None
    error: bool = None


def get_test_class_name(test):
    """Compute the test class name from the test object."""
    return f'{test.__module__}.{test.__class__.__name__}'


def filename_to_suite_name_parts(filename):
    # lop off whatever portion of the path we have in common
    # with the current working directory; crude, but about as
    # much as we can do :(
    filenameParts = Path(filename).parts
    cwdParts = Path.cwd().parts
    longest = min(len(filenameParts), len(cwdParts))
    for i in range(longest):
        if filenameParts[i] != cwdParts[i]:
            break

    if i < len(filenameParts) - 1:

        # The real package name couldn't have a '.' in it. This
        # makes sense for the common egg naming patterns, and
        # will still work in other cases

        suiteNameParts = []
        for part in reversed(filenameParts[i:-1]):
            if '.' in part:
                break
            suiteNameParts.insert(0, part)

        # don't lose the filename, which would have a . in it
        suiteNameParts.append(filenameParts[-1])
        return suiteNameParts


def parse_doc_file_case(test):
    if not isinstance(test, doctest.DocFileCase):
        return None, None, None

    filename = test._dt_test.filename
    suiteNameParts = filename_to_suite_name_parts(filename)
    testSuite = f'doctest-{"-".join(suiteNameParts)}'
    testName = test._dt_test.name
    testClassName = '.'.join(suiteNameParts[:-1])
    return testSuite, testName, testClassName


def parse_doc_test_case(test):
    if not isinstance(test, doctest.DocTestCase):
        return None, None, None

    testDottedNameParts = test._dt_test.name.split('.')
    testClassName = get_test_class_name(test)
    testSuite = testClassName = '.'.join(testDottedNameParts[:-1])
    testName = testDottedNameParts[-1]
    return testSuite, testName, testClassName


def parse_manuel(test):
    if not (HAVE_MANUEL and isinstance(test, manuel.testing.TestCase)):
        return None, None, None
    filename = test.regions.location
    suiteNameParts = filename_to_suite_name_parts(filename)
    testSuite = f'manuel-{"-".join(suiteNameParts)}'
    testName = suiteNameParts[-1]
    testClassName = '.'.join(suiteNameParts[:-1])
    return testSuite, testName, testClassName


def parse_startup_failure(test):
    if not isinstance(test, StartUpFailure):
        return None, None, None
    testModuleName = test.module
    return testModuleName, 'Startup', testModuleName


def parse_unittest(test):
    testId = test.id()
    if testId is None:
        return None, None, None
    testClassName = get_test_class_name(test)
    testSuite = testClassName
    testName = testId[len(testClassName) + 1:]
    return testSuite, testName, testClassName


class XMLOutputFormattingWrapper:
    """Output formatter which delegates to another formatter for all
    operations, but also prepares an element tree of test output.
    """

    def __init__(self, delegate, folder):
        self.delegate = delegate
        self._testSuites = {}  # test class -> list of test names
        self.folder = folder

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def test_failure(self, test, seconds, exc_info, stdout=None, stderr=None):
        self._record(test, seconds, failure=exc_info)
        # stdout and stderr are only passed into us when using buffering
        # (--buffer). self.delegate also comes from zope.testrunner then.
        if stdout is None and stderr is None:
            # the normal case
            return self.delegate.test_failure(test, seconds, exc_info)
        return self.delegate.test_failure(
            test, seconds, exc_info, stdout=stdout, stderr=stderr
        )

    def test_error(self, test, seconds, exc_info, stdout=None, stderr=None):
        self._record(test, seconds, error=exc_info)
        if stdout is None and stderr is None:
            # the normal case
            return self.delegate.test_error(test, seconds, exc_info)
        return self.delegate.test_error(
            test, seconds, exc_info, stdout=stdout, stderr=stderr
        )

    def test_success(self, test, seconds):
        self._record(test, seconds)
        return self.delegate.test_success(test, seconds)

    def import_errors(self, import_errors):
        if import_errors:
            for test in import_errors:
                self._record(test, 0, error=test.exc_info)
        return self.delegate.import_errors(import_errors)

    def _record(self, test, seconds, failure=None, error=None):
        for parser in [parse_doc_file_case,
                       parse_doc_test_case,
                       parse_manuel,
                       parse_startup_failure,
                       parse_unittest]:
            testSuite, testName, testClassName = parser(test)
            if (testSuite, testName, testClassName) != (None, None, None):
                break

        if (testSuite, testName, testClassName) == (None, None, None):
            raise TypeError(
                'Unknown test type: Could not compute testSuite, testName,'
                f' testClassName: {test!r}'
            )

        suite = self._testSuites.setdefault(testSuite, TestSuiteInfo())
        suite.testCases.append(TestCaseInfo(
            test, seconds, testClassName, testName, failure, error))

        if failure is not None:
            suite.failures += 1

        if error is not None:
            suite.errors += 1

        if seconds:
            suite.time += seconds

    def writeXMLReports(self, properties={}):

        timestamp = datetime.now().isoformat()
        hostname = socket.gethostname()

        reportsDir = self.folder / 'testreports'
        reportsDir.mkdir(exist_ok=True)

        for name, suite in self._testSuites.items():
            filename = reportsDir / f'{name}.xml'

            testSuiteNode = ElementTree.Element('testsuite')

            testSuiteNode.set('tests', str(suite.tests))
            testSuiteNode.set('errors', str(suite.errors))
            testSuiteNode.set('failures', str(suite.failures))
            testSuiteNode.set('hostname', hostname)
            testSuiteNode.set('name', name)
            testSuiteNode.set('time', str(suite.time))
            testSuiteNode.set('timestamp', timestamp)

            propertiesNode = ElementTree.Element('properties')
            testSuiteNode.append(propertiesNode)

            for k, v in properties.items():
                propertyNode = ElementTree.Element('property')
                propertiesNode.append(propertyNode)

                propertyNode.set('name', k)
                propertyNode.set('value', v)

            for testCase in suite.testCases:
                testCaseNode = ElementTree.Element('testcase')
                testSuiteNode.append(testCaseNode)

                testCaseNode.set('classname', testCase.testClassName)
                testCaseNode.set('name', testCase.testName)
                testCaseNode.set('time', str(testCase.time))

                if testCase.error:
                    errorNode = ElementTree.Element('error')
                    testCaseNode.append(errorNode)

                    try:
                        excType, excInstance, tb = testCase.error
                        errorMessage = str(excInstance)
                        stackTrace = ''.join(traceback.format_tb(tb))
                    finally:  # Avoids a memory leak
                        del tb

                    errorNode.set('message', errorMessage.split('\n')[0])
                    errorNode.set('type', str(excType))
                    text = (errorMessage + '\n\n' + stackTrace)
                    errorNode.text = text

                if testCase.failure:

                    failureNode = ElementTree.Element('failure')
                    testCaseNode.append(failureNode)

                    try:
                        excType, excInstance, tb = testCase.failure
                        errorMessage = str(excInstance)
                        stackTrace = ''.join(traceback.format_tb(tb))
                    except UnicodeEncodeError:
                        errorMessage = 'Could not extract error str ' \
                            'for unicode error'
                        stackTrace = ''.join(traceback.format_tb(tb))
                    finally:  # Avoids a memory leak
                        del tb

                    failureNode.set('message', errorMessage.split('\n')[0])
                    failureNode.set('type', str(excType))
                    text = f'{errorMessage}\n\n{stackTrace}'
                    failureNode.text = text

            # We don't have a good way to capture these yet, so they are empty:
            systemOutNode = ElementTree.Element('system-out')
            testSuiteNode.append(systemOutNode)
            systemErrNode = ElementTree.Element('system-err')
            testSuiteNode.append(systemErrNode)

            # indent the XML structure
            with suppress(AttributeError):
                ElementTree.indent(testSuiteNode)
            text = ElementTree.tostring(testSuiteNode).decode('utf-8')

            # Write file
            with open(filename, 'w') as outputFile:
                outputFile.write(text)
