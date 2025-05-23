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
"""Test execution
"""
import errno
import gc
import io
import os
import pprint
import queue
import re
import subprocess
import sys
import threading
import time
import traceback
import unittest
import warnings
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import zope.testrunner
import zope.testrunner._doctest
import zope.testrunner.coverage
import zope.testrunner.debug
import zope.testrunner.filter
import zope.testrunner.garbagecollection
import zope.testrunner.interfaces
import zope.testrunner.listing
import zope.testrunner.logsupport
import zope.testrunner.process
import zope.testrunner.profiling
import zope.testrunner.selftest
import zope.testrunner.shuffle
import zope.testrunner.statistics
import zope.testrunner.tb_format
from zope.testrunner import threadsupport
from zope.testrunner.find import _layer_name_cache
from zope.testrunner.find import import_name
from zope.testrunner.find import name_from_layer
from zope.testrunner.formatter import XMLOutputFormattingWrapper
from zope.testrunner.layer import EmptyLayer
from zope.testrunner.layer import EmptySuite
from zope.testrunner.layer import UnitTests
from zope.testrunner.options import get_options
from zope.testrunner.refcount import TrackRefs

from .digraph import DiGraph
from .util import is_jython
from .util import uses_refcounts


class UnexpectedSuccess(Exception):
    pass


PYREFCOUNT_PATTERN = re.compile(r'\[[0-9]+ refs\]')


class SubprocessError(Exception):
    """An error occurred when running a subprocess
    """

    def __init__(self, reason, stderr):
        self.reason = reason
        self.stderr = stderr

    def __str__(self):
        return f'{self.reason}: {self.stderr}'


class CanNotTearDown(Exception):
    "Couldn't tear down a test"


class Runner:
    """The test runner.

    It is the central point of this package and responsible for finding and
    executing tests as well as configuring itself from the (command-line)
    options passed into it.

    .. versionchanged:: 4.8.0
       Add the *warnings* keyword argument. If this is ``None`` (the default)
       and the user hasn't configured Python otherwise with command-line
       arguments or environment variables, we will enable the default
       warnings, including ``DeprecationWarning``, when running tests.
       Otherwise, it can be any string acceptable to
       :func:`warnings.simplefilter` and that filter will be in effect while
       running tests.

    """

    def __init__(self, defaults=None, args=None, found_suites=None,
                 options=None, script_parts=None, cwd=None,
                 warnings=None):
        if defaults is None:
            self.defaults = []
        else:
            self.defaults = defaults
        self.args = args
        self.found_suites = found_suites
        self.options = options
        self.script_parts = script_parts
        self.cwd = cwd
        self.failed = True
        if warnings is None and not sys.warnoptions:
            # even if DeprecationWarnings are ignored by default
            # print them anyway unless other warnings settings are
            # specified by the warnings arg or the -W python flag
            self.warnings = 'default'
        else:
            # here self.warnings is set either to the value passed
            # to the warnings args or to None.
            # If the user didn't pass a value self.warnings will
            # be None. This means that the behavior is unchanged
            # and depends on the values passed to -W.
            self.warnings = warnings

        self.ran = 0
        self.skipped = []
        self.failures = []
        self.errors = []
        self.import_errors = []

        self.show_report = True
        self.do_run_tests = True

        self.features = []

        self.tests_by_layer_name = {}

    def ordered_layers(self):
        if (self.options.processes > 1 and not self.options.resume_layer):
            # if we want multiple processes, we need a fake layer as first
            # to start spreading out layers/tests to subprocesses
            # but only if this is not in the subprocess
            yield (name_from_layer(EmptyLayer), EmptyLayer, EmptySuite())

        layer_names = {layer_from_name(layer_name): layer_name
                       for layer_name in self.tests_by_layer_name}
        for layer in order_by_bases(layer_names):
            layer_name = layer_names[layer]
            yield layer_name, layer, self.tests_by_layer_name[layer_name]

    def register_tests(self, tests):
        """Registers tests."""
        # XXX To support multiple features that find tests this shouldn't be
        # an update but merge the various layers individually.
        self.tests_by_layer_name.update(tests)

    def run(self):
        self.configure()
        if self.options.fail:
            return True

        # XXX Hacky to support existing code.
        self.layer_name_cache = _layer_name_cache
        self.layer_name_cache.clear()

        with self._enabled_warnings():
            # Enable warnings during setup so that
            # warnings raised on import (which we do for test
            # discover) can be reported.

            # Global setup
            for feature in self.features:
                feature.global_setup()

            # Late setup
            #
            # Some system tools like profilers are really bad with stack
            # frames.  E.g. hotshot doesn't like it when we leave the stack
            # frame that we called start() from.
            for feature in self.features:
                feature.late_setup()

            try:
                if self.do_run_tests:
                    self.run_tests()
            finally:
                # Early teardown
                for feature in reversed(self.features):
                    feature.early_teardown()
                # Global teardown
                for feature in reversed(self.features):
                    feature.global_teardown()

            if self.show_report:
                for feature in self.features:
                    feature.report()

        if self.options.xmlOutput:
            self.options.output.writeXMLReports()

    def configure(self):
        if self.args is None:
            self.args = sys.argv[:]
        # Check to see if we are being run as a subprocess. If we are,
        # then use the resume-layer and defaults passed in.
        if len(self.args) > 1 and self.args[1] == '--resume-layer':
            self.args.pop(1)
            resume_layer = self.args.pop(1)
            resume_number = int(self.args.pop(1))
            self.defaults = []
            while len(self.args) > 1 and self.args[1] == '--default':
                self.args.pop(1)
                self.defaults.append(self.args.pop(1))

            sys.stdin = FakeInputContinueGenerator()
        else:
            resume_layer = resume_number = None

        options = get_options(self.args, self.defaults)

        options.testrunner_defaults = self.defaults
        options.resume_layer = resume_layer
        options.resume_number = resume_number

        if options.xmlOutput:
            folder = Path(options.xmlOutput).resolve()
            folder.mkdir(parents=True, exist_ok=True)
            options.output = XMLOutputFormattingWrapper(
                options.output, folder=folder)

        self.options = options

        self.features.append(zope.testrunner.selftest.SelfTest(self))
        self.features.append(zope.testrunner.logsupport.Logging(self))
        self.features.append(zope.testrunner.coverage.Coverage(self))
        self.features.append(zope.testrunner._doctest.DocTest(self))
        self.features.append(zope.testrunner.profiling.Profiling(self))
        if is_jython:
            # Jython GC support is not yet implemented
            pass
        else:
            self.features.append(
                zope.testrunner.garbagecollection.Threshold(self))
            self.features.append(
                zope.testrunner.garbagecollection.Debug(self))

        self.features.append(zope.testrunner.find.Find(self))
        self.features.append(zope.testrunner.shuffle.Shuffle(self))
        self.features.append(zope.testrunner.process.SubProcess(self))
        self.features.append(zope.testrunner.filter.Filter(self))
        self.features.append(zope.testrunner.listing.Listing(self))
        self.features.append(
            zope.testrunner.statistics.Statistics(self))
        self.features.append(zope.testrunner.tb_format.Traceback(self))

        # Remove all features that aren't activated
        self.features = [f for f in self.features if f.active]

    @contextmanager
    def _enabled_warnings(self):
        """
        A context manager to enable warnings as configured.
        """
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings(
                        'module',
                        category=DeprecationWarning,
                        message=r'Please use assert\w+ instead.')
            yield

    def run_tests(self):
        """Run all tests that were registered.

        Returns True if there where failures or False if all tests passed.

        """
        setup_layers = {}
        layers_to_run = list(self.ordered_layers())
        should_resume = False

        while layers_to_run:
            layer_name, layer, tests = layers_to_run[0]
            for feature in self.features:
                feature.layer_setup(layer)
            try:
                self.ran += run_layer(self.options, layer_name, layer, tests,
                                      setup_layers, self.failures, self.errors,
                                      self.skipped, self.import_errors)
            except zope.testrunner.interfaces.EndRun:
                self.failed = True
                break
            except CanNotTearDown:
                if not self.options.resume_layer:
                    should_resume = True
                    break

            layers_to_run.pop(0)
            if self.options.processes > 1:
                should_resume = True
                break

            if self.options.stop_on_error and (self.failures or self.errors):
                break

        if should_resume:
            if layers_to_run:
                self.ran += resume_tests(
                    self.script_parts, self.options, self.features,
                    layers_to_run, self.failures, self.errors,
                    self.skipped, self.cwd)

        if setup_layers:
            if self.options.resume_layer is None:
                self.options.output.info("Tearing down left over layers:")
            tear_down_unneeded(
                self.options, (), setup_layers, self.errors, optional=True)

        self.failed = bool(self.import_errors or self.failures or self.errors)


def handle_layer_failure(failure_type, output, errors):
    if hasattr(output, 'layer_failure'):
        output.layer_failure(failure_type.subunit_label, sys.exc_info())
    else:
        f = StringIO()
        traceback.print_exc(file=f)
        output.error(f.getvalue())
    errors.append((failure_type, sys.exc_info()))


def run_tests(options, tests, name, failures, errors, skipped, import_errors):
    repeat = options.repeat or 1
    repeat_range = iter(range(repeat))
    ran = 0

    output = options.output

    if is_jython:
        # Jython has no GC suppport - set count to 0
        lgarbage = 0
    else:
        gc.collect()
        lgarbage = len(gc.garbage)

    if options.report_refcounts:
        if options.verbose:
            # XXX This code path is untested
            track = TrackRefs()
        rc = sys.gettotalrefcount()

    for iteration in repeat_range:
        if repeat > 1:
            output.info("Iteration %d" % (iteration + 1))

        if options.verbose > 0 or options.progress:
            output.info('  Running:')
        result = TestResult(options, tests, layer_name=name)

        t = time.time()

        if options.post_mortem:
            # post-mortem debugging
            for test in tests:
                if result.shouldStop:
                    break
                expecting_failure = (
                    getattr(test, "__unittest_expecting_failure__", False)
                    or getattr(
                        getattr(test, test._testMethodName),
                        "__unittest_expecting_failure__",
                        False)
                )
                result.startTest(test)
                state = test.__dict__.copy()
                try:
                    try:
                        test.debug()
                    except KeyboardInterrupt:
                        raise
                    except unittest.SkipTest as e:
                        result.addSkip(test, str(e))
                    except BaseException:
                        exc_info = (
                            sys.exc_info()[:2]
                            + (sys.exc_info()[2].tb_next, )
                        )
                        if expecting_failure:
                            result.addExpectedFailure(test, exc_info)
                        else:
                            result.addError(test, exc_info)
                    else:
                        if expecting_failure:
                            result.addUnexpectedSuccess(test)
                        else:
                            result.addSuccess(test)
                finally:
                    result.stopTest(test)
                test.__dict__.clear()
                test.__dict__.update(state)

        else:
            # normal
            for test in tests:
                if result.shouldStop:
                    break
                state = test.__dict__.copy()
                test(result)
                test.__dict__.clear()
                test.__dict__.update(state)

        t = time.time() - t
        output.stop_tests()
        failures.extend(result.failures)
        n_failures = len(result.failures)
        failures.extend([(s, None) for s in result.unexpectedSuccesses])
        n_failures += len(result.unexpectedSuccesses)
        skipped.extend(result.skipped)
        errors.extend(result.errors)
        output.summary(n_tests=result.testsRun,
                       n_failures=n_failures,
                       n_errors=len(result.errors) + len(import_errors),
                       n_seconds=t,
                       n_skipped=len(result.skipped))
        ran = result.testsRun

        if is_jython:
            lgarbage = 0
        else:
            gc.collect()
            if len(gc.garbage) > lgarbage:
                output.garbage(gc.garbage[lgarbage:])
                lgarbage = len(gc.garbage)

        if options.report_refcounts:

            # If we are being tested, we don't want stdout itself to
            # foul up the numbers. :)
            try:
                sys.stdout.getvalue()
            except AttributeError:
                pass

            prev = rc
            rc = sys.gettotalrefcount()
            if options.verbose:
                track.update()
                if iteration > 0:
                    output.detailed_refcounts(track, rc, prev)
                else:
                    track.delta = None
            elif iteration > 0:
                output.refcounts(rc, prev)

    return ran


def run_layer(options, layer_name, layer, tests, setup_layers,
              failures, errors, skipped, import_errors):

    output = options.output
    gathered = []
    gather_layers(layer, gathered)
    needed = {ly: 1 for ly in gathered}
    if options.resume_number != 0:
        output.info("Running %s tests:" % layer_name)
    tear_down_unneeded(options, needed, setup_layers, errors)

    if options.resume_layer is not None:
        output.info_suboptimal("  Running in a subprocess.")

    try:
        setup_layer(options, layer, setup_layers)
    except zope.testrunner.interfaces.EndRun:
        raise
    except MemoryError:
        raise
    except Exception:
        handle_layer_failure(SetUpLayerFailure(layer), output, errors)
        return 0
    else:
        return run_tests(options, tests, layer_name, failures, errors, skipped,
                         import_errors)


class SetUpLayerFailure(unittest.TestCase):

    subunit_label = 'setUp'

    def __init__(self, layer):
        super().__init__()
        self.layer = layer

    def runTest(self):
        pass

    def __str__(self):
        return "Layer: %s.setUp" % (name_from_layer(self.layer))


class TearDownLayerFailure(unittest.TestCase):

    subunit_label = 'tearDown'

    def __init__(self, layer):
        super().__init__()
        self.layer = layer

    def runTest(self):
        pass

    def __str__(self):
        return "Layer: %s.tearDown" % (name_from_layer(self.layer))


def spawn_layer_in_subprocess(result, script_parts, options, features,
                              layer_name, layer, failures, errors, skipped,
                              resume_number, cwd=None):
    output = options.output
    child = None
    try:
        # BBB
        if script_parts is None:
            script_parts = zope.testrunner._script_parts()
        args = [sys.executable]
        args.extend(script_parts)
        args.extend(['--resume-layer', layer_name, str(resume_number)])
        for d in options.testrunner_defaults:
            args.extend(['--default', d])

        args.extend(options.original_testrunner_args[1:])

        debugargs = args  # save them before messing up for windows
        if sys.platform.startswith('win'):
            args = args[0] + ' ' + ' '.join([
                ('"' + a.replace('\\', '\\\\').replace('"', '\\"') + '"')
                for a in args[1:]])

        for feature in features:
            feature.layer_setup(layer)

        child = subprocess.Popen(
            args, shell=False, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd,
            close_fds=not sys.platform.startswith('win'))

        def reader_thread(f, buf):
            buf.append(f.read())

        # Start reading stderr in a thread.  This means we don't hang if the
        # subprocess writes more to stderr than the pipe capacity.
        stderr_buf = []
        stderr_thread = threading.Thread(
            target=reader_thread, args=(child.stderr, stderr_buf))
        stderr_thread.daemon = True
        stderr_thread.start()

        while True:
            try:
                while True:
                    # We use readline() instead of iterating over stdout
                    # because it appears that iterating over stdout causes a
                    # lot more buffering to take place (probably so it can
                    # return its lines as a batch). We don't want too much
                    # buffering because this foils automatic and human monitors
                    # trying to verify that the subprocess is still alive.
                    line = child.stdout.readline()
                    if not line:
                        break
                    result.write(line)
            except OSError as e:
                if e.errno == errno.EINTR:
                    # If the subprocess dies before we finish reading its
                    # output, a SIGCHLD signal can interrupt the reading.
                    # The correct thing to to in that case is to retry.
                    continue
                output.error(
                    "Error reading subprocess output for %s" % layer_name)
                output.info(str(e))
            else:
                break

        # Now we should be able to finish reading stderr.
        stderr_thread.join()
        errlines = stderr_buf[0].splitlines()
        erriter = iter(errlines)
        nfail = nerr = 0
        for line in erriter:
            try:
                result.num_ran, nfail, nerr = map(int, line.strip().split())
            except ValueError:
                continue
            else:
                break
        else:
            errmsg = "Could not communicate with subprocess!"
            errors.append(("subprocess for %s" % layer_name, None))
            if options.verbose >= 1:
                errmsg += "\nChild command line: %s" % debugargs
            if (options.verbose >= 2 or
                    (options.verbose == 1 and len(errlines) < 20)):
                errmsg += ("\nChild stderr was:\n" +
                           "\n".join("  " + line.decode('utf-8', 'replace')
                                     for line in errlines))
            elif options.verbose >= 1:
                errmsg += ("\nChild stderr was:\n" +
                           "\n".join("  " + line.decode('utf-8', 'replace')
                                     for line in errlines[:10]) +
                           "\n...\n" +
                           "\n".join("  " + line.decode('utf-8', 'replace')
                                     for line in errlines[-10:]))
            output.error_with_banner(errmsg)

        while nfail > 0:
            nfail -= 1
            # Doing erriter.next().strip() confuses the 2to3 fixer, so
            # we need to do it on a separate line. Also, in python 3 this
            # returns bytes, so we decode it.
            next_fail = next(erriter)
            failures.append((next_fail.strip().decode(), None))
        while nerr > 0:
            nerr -= 1
            # Doing erriter.next().strip() confuses the 2to3 fixer, so
            # we need to do it on a separate line. Also, in python 3 this
            # returns bytes, so we decode it.
            next_err = next(erriter)
            errors.append((next_err.strip().decode(), None))

    finally:
        result.done = True
        if child is not None:
            # Regardless of whether the process ran to completion, we
            # must properly cleanup the process to avoid
            # `ResourceWarning: subprocess XXX is still alive` and
            # `ResourceWarning: unclosed file` for its stdout and
            # stderr.
            child.kill()
            child.communicate()


def _get_output_buffer(stream):
    """Get a binary-safe version of a stream."""
    try:
        fileno = stream.fileno()
    except (io.UnsupportedOperation, AttributeError):
        pass
    else:
        # Win32 mangles \r\n to \n and that breaks streams.  See
        # https://bugs.launchpad.net/bugs/505078.
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.setmode(fileno, os.O_BINARY)
    try:
        stream.write(b'')
    except TypeError:
        return stream.buffer
    return stream


class AbstractSubprocessResult:
    """A result of a subprocess layer run."""

    num_ran = 0
    done = False

    def __init__(self, layer_name, queue):
        self.layer_name = layer_name
        self.queue = queue
        self.stdout = []

    def write(self, out):
        """Receive a line of the subprocess out."""


class DeferredSubprocessResult(AbstractSubprocessResult):
    """Keeps stdout around for later processing,"""

    def write(self, out):
        if not _is_dots(out):
            self.stdout.append(out)


class ImmediateSubprocessResult(AbstractSubprocessResult):
    """Sends complete output to queue."""

    def __init__(self, layer_name, queue):
        super().__init__(layer_name, queue)
        self.stream = _get_output_buffer(sys.stdout)

    def write(self, out):
        self.stream.write(out)
        # Help keep-alive monitors (human or automated) keep up-to-date.
        self.stream.flush()


_is_dots = re.compile(br'\.+(\r\n?|\n)').match  # Windows sneaks in a \r\n.


class KeepaliveSubprocessResult(AbstractSubprocessResult):
    "Keeps stdout for later processing; sends marks to queue to show activity."

    _done = False

    def _set_done(self, value):
        self._done = value
        assert value, 'Internal error: unexpectedly setting done to False'
        self.queue.put((self.layer_name, ' LAYER FINISHED'))
    done = property(lambda self: self._done, _set_done)

    def write(self, out):
        if _is_dots(out):
            self.queue.put((self.layer_name, out.strip()))
        else:
            self.stdout.append(out)


def resume_tests(script_parts, options, features, layers, failures, errors,
                 skipped, cwd=None):
    results = []
    stdout_queue = None
    if options.processes == 1:
        result_factory = ImmediateSubprocessResult
    elif (options.verbose > 1 and
            not options.subunit and not options.subunit_v2):
        result_factory = KeepaliveSubprocessResult
        stdout_queue = queue.Queue()
    else:
        result_factory = DeferredSubprocessResult
    resume_number = int(options.processes > 1)
    ready_threads = []
    for layer_name, layer, tests in layers:
        result = result_factory(layer_name, stdout_queue)
        results.append(result)
        ready_threads.append(threading.Thread(
            target=spawn_layer_in_subprocess,
            args=(result, script_parts, options, features, layer_name, layer,
                  failures, errors, skipped, resume_number, cwd)))
        resume_number += 1

    # Now start a few threads at a time.
    running_threads = []
    results_iter = iter(results)
    current_result = next(results_iter)
    last_layer_intermediate_output = None
    output = None
    # Get an object that (only) accepts bytes
    stdout = _get_output_buffer(sys.stdout)
    while ready_threads or running_threads:
        while len(running_threads) < options.processes and ready_threads:
            thread = ready_threads.pop(0)
            thread.start()
            running_threads.append(thread)

        for index, thread in reversed(list(enumerate(running_threads))):
            if not thread.is_alive():
                del running_threads[index]

        # Clear out any messages in queue
        while stdout_queue is not None:
            previous_output = output
            try:
                layer_name, output = stdout_queue.get(False)
            except queue.Empty:
                break
            if layer_name != last_layer_intermediate_output:
                # Clarify what layer is reporting activity.
                if previous_output is not None:
                    stdout.write(b']\n')
                stdout.write(
                    ('[Parallel tests running in '
                     '%s:\n  ' % (layer_name,)).encode('utf-8'))
                last_layer_intermediate_output = layer_name
            if not isinstance(output, bytes):
                output = output.encode('utf-8')
            stdout.write(output)
        # Display results in the order they would have been displayed, had the
        # work not been done in parallel.
        while current_result and current_result.done:
            if output is not None:
                stdout.write(b']\n')
                output = None
            stdout.writelines(current_result.stdout)

            try:
                current_result = next(results_iter)
            except StopIteration:
                current_result = None

        # Help keep-alive monitors (human or automated) keep up-to-date.
        stdout.flush()
        time.sleep(0.01)  # Keep the loop from being too tight.

    # Return the total number of tests run.
    return sum(r.num_ran for r in results)


def tear_down_unneeded(options, needed, setup_layers, errors, optional=False):
    # Tear down any layers not needed for these tests. The unneeded layers
    # might interfere.
    unneeded = [layer for layer in setup_layers if layer not in needed]
    unneeded = order_by_bases(unneeded)
    unneeded.reverse()
    output = options.output
    for layer in unneeded:
        output.start_tear_down(name_from_layer(layer))
        t = time.time()
        try:
            try:
                if hasattr(layer, 'tearDown'):
                    layer.tearDown()
            except NotImplementedError:
                output.tear_down_not_supported()
                if not optional:
                    raise CanNotTearDown(layer)
            except MemoryError:
                raise
            except Exception:
                handle_layer_failure(
                    TearDownLayerFailure(layer), output, errors)
            else:
                output.stop_tear_down(time.time() - t)
        finally:
            del setup_layers[layer]


cant_pm_in_subprocess_message = """
Can't post-mortem debug when running a layer as a subprocess!
Try running layer %r by itself.
"""


def setup_layer(options, layer, setup_layers):
    assert layer is not object
    output = options.output
    if layer not in setup_layers:
        for base in layer.__bases__:
            if base is not object:
                setup_layer(options, base, setup_layers)
        output.start_set_up(name_from_layer(layer))
        t = time.time()
        if hasattr(layer, 'setUp'):
            try:
                layer.setUp()
            except MemoryError:
                raise
            except Exception:
                if options.post_mortem:
                    if options.resume_layer:
                        options.output.error_with_banner(
                            cant_pm_in_subprocess_message
                            % options.resume_layer)
                        raise
                    else:
                        zope.testrunner.debug.post_mortem(
                            sys.exc_info())
                else:
                    raise

        output.stop_set_up(time.time() - t)
        setup_layers[layer] = 1


class TestResult(unittest.TestResult):

    def __init__(self, options, tests, layer_name=None):
        unittest.TestResult.__init__(self)
        self.options = options
        # Calculate our list of relevant layers we need to call testSetUp
        # and testTearDown on.
        layers = []
        gather_layers(layer_from_name(layer_name), layers)
        self.layers = order_by_bases(layers)
        count = 0
        for test in tests:
            count += test.countTestCases()
        self.count = count
        self._stdout_buffer = None
        self._stderr_buffer = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def testSetUp(self):
        """A layer may define a setup method to be called before each
        individual test.
        """
        for layer in self.layers:
            if hasattr(layer, 'testSetUp'):
                layer.testSetUp()

    def testTearDown(self):
        """A layer may define a teardown method to be called after each
           individual test.

           This is useful for clearing the state of global
           resources or resetting external systems such as relational
           databases or daemons.
        """
        for layer in self.layers[-1::-1]:
            if hasattr(layer, 'testTearDown'):
                layer.testTearDown()

    def _makeBufferedStdStream(self):
        """Make a buffered stream to replace a standard stream."""
        # The returned stream needs to have a 'buffer' attribute, since
        # some tests may expect that to exist on standard streams, and a
        # 'getvalue' method for the convenience of _restoreStdStreams.
        # This requires some care.
        class BufferedStandardStream(io.TextIOWrapper):
            def getvalue(self):
                return self.buffer.getvalue().decode(
                    encoding=self.encoding, errors=self.errors)

        return BufferedStandardStream(
            io.BytesIO(), newline='\n', write_through=True)

    def _setUpStdStreams(self):
        """Set up buffered standard streams, if requested."""
        if self.options.buffer:
            if self._stdout_buffer is None:
                self._stdout_buffer = self._makeBufferedStdStream()
            if self._stderr_buffer is None:
                self._stderr_buffer = self._makeBufferedStdStream()
            sys.stdout = self._stdout_buffer
            sys.stderr = self._stderr_buffer

    def _restoreStdStreams(self):
        """Restore the buffered standard streams and return any contents."""
        if self.options.buffer:
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._stdout_buffer.seek(0)
            self._stdout_buffer.truncate(0)
            self._stderr_buffer.seek(0)
            self._stderr_buffer.truncate(0)
            return stdout, stderr
        else:
            return None, None

    def startTest(self, test):
        self._test_state = test.__dict__.copy()
        self.testSetUp()
        unittest.TestResult.startTest(self, test)
        testsRun = self.testsRun - 1  # subtract the one the base class added
        count = test.countTestCases()
        self.testsRun = testsRun + count

        self.options.output.start_test(test, self.testsRun, self.count)

        self._threads = threadsupport.enumerate()
        self._start_time = time.time()

        self._setUpStdStreams()

    def addSuccess(self, test):
        self._restoreStdStreams()
        t = max(time.time() - self._start_time, 0.0)
        self.options.output.test_success(test, t)

    def addSkip(self, test, reason):
        if not hasattr(self, "_test_state"):
            # ``startTest`` was not called -- set up extected state
            self._test_state = test.__dict__
            count = test.countTestCases()
            self.testsRun += count
            self.options.output.start_test(test, self.testsRun, self.count)
            self._threads = threadsupport.enumerate()
            if not hasattr(self, "_start_time"):
                self._start_time = time.time()
        else:
            self._restoreStdStreams()
        unittest.TestResult.addSkip(self, test, reason)
        self.options.output.test_skipped(test, reason)

    def addSubTest(self, test, subtest, exc_info):
        if exc_info is None:
            return
        stdout, stderr = self._restoreStdStreams()
        outp = self.options.output
        report = (outp.test_failure
                  if issubclass(exc_info[0], test.failureException)
                  else outp.test_error)
        report(subtest, time.time() - self._start_time,
               exc_info, stdout=stdout, stderr=stderr)

        unittest.TestResult.addSubTest(self, test, subtest, exc_info)

        if self.options.post_mortem:
            if self.options.resume_layer:
                self.options.output.error_with_banner(
                    "Can't post-mortem debug when running a layer as"
                    " a subprocess!")
            else:
                zope.testrunner.debug.post_mortem(exc_info)
        elif self.options.stop_on_error:
            self.stop()

    def addError(self, test, exc_info):
        stdout, stderr = self._restoreStdStreams()
        self.options.output.test_error(test, time.time() - self._start_time,
                                       exc_info,
                                       stdout=stdout, stderr=stderr)

        unittest.TestResult.addError(self, test, exc_info)

        if self.options.post_mortem:
            if self.options.resume_layer:
                self.options.output.error_with_banner("Can't post-mortem debug"
                                                      " when running a layer"
                                                      " as a subprocess!")
            else:
                zope.testrunner.debug.post_mortem(exc_info)
        elif self.options.stop_on_error:
            self.stop()

    def addFailure(self, test, exc_info):
        stdout, stderr = self._restoreStdStreams()
        self.options.output.test_failure(test, time.time() - self._start_time,
                                         exc_info,
                                         stdout=stdout, stderr=stderr)

        unittest.TestResult.addFailure(self, test, exc_info)

        if self.options.post_mortem:
            # XXX: mgedmin: why isn't there a resume_layer check here like
            # in addError?
            zope.testrunner.debug.post_mortem(exc_info)
        elif self.options.stop_on_error:
            self.stop()

    def addExpectedFailure(self, test, exc_info):
        self._restoreStdStreams()
        t = max(time.time() - self._start_time, 0.0)
        self.options.output.test_success(test, t)

        unittest.TestResult.addExpectedFailure(self, test, exc_info)

    def addUnexpectedSuccess(self, test):
        stdout, stderr = self._restoreStdStreams()
        self.options.output.test_error(
            test, time.time() - self._start_time,
            (UnexpectedSuccess, UnexpectedSuccess(), None),
            stdout=stdout, stderr=stderr)

        unittest.TestResult.addUnexpectedSuccess(self, test)

        if self.options.post_mortem:
            if self.options.resume_layer:
                self.options.output.error_with_banner("Can't post-mortem debug"
                                                      " when running a layer"
                                                      " as a subprocess!")
            else:
                self.options.output.error_with_banner("Can't post-mortem debug"
                                                      " an unexpected success")
        elif self.options.stop_on_error:
            self.stop()

    def stopTest(self, test):
        self.testTearDown()
        # Without clearing, cyclic garbage referenced by the test
        # would be reported in the following test.
        test.__dict__.clear()
        test.__dict__.update(self._test_state)
        del self._test_state
        cycles = None
        if (uses_refcounts and self.options.gc_after_test and
                self.options.verbose >= 4):
            gc_opts = gc.get_debug()
            gc.set_debug(gc.DEBUG_SAVEALL)
            gc.collect()
            if gc.garbage:
                g = DiGraph(gc.garbage)
                for obj in gc.garbage:
                    g.add_neighbors(obj, gc.get_referents(obj))
                cycles = [[repr_lines(o) for o in c] for c in g.sccs()]
                del gc.garbage[:]
                g = obj = None  # avoid to hold cyclic garbage
            gc.set_debug(gc_opts)
        gccount = gc.collect() \
            if uses_refcounts and self.options.gc_after_test else 0
        self.options.output.stop_test(test, gccount)

        if cycles:
            self.options.output.test_cycles(test, cycles)

        if is_jython:
            pass
        else:
            if gc.garbage:
                self.options.output.test_garbage(test, gc.garbage)
                # TODO: Perhaps eat the garbage here, so that the garbage isn't
                #       printed for every subsequent test.

        # Did the test leave any new threads behind?
        new_threads = []
        for t in threadsupport.enumerate():
            if t.is_alive() and t not in self._threads:
                if not any([re.match(p, t.name)
                            for p in self.options.ignore_new_threads]):
                    new_threads.append(t)

        if new_threads:
            self.options.output.test_threads(test, new_threads)


def layer_from_name(layer_name):
    """Return the layer for the corresponding layer_name by discovering
       and importing the necessary module if necessary.

       Note that a name -> layer cache is maintained by name_from_layer
       to allow locating layers in cases where it would otherwise be
       impossible.
    """
    if layer_name in _layer_name_cache:
        return _layer_name_cache[layer_name]
    layer_names = layer_name.split('.')
    layer_module, module_layer_name = layer_names[:-1], layer_names[-1]
    module_name = '.'.join(layer_module)
    module = import_name(module_name)
    try:
        return getattr(module, module_layer_name)
    except AttributeError:
        # the default error is very uninformative:
        #   AttributeError: 'module' object has no attribute 'DemoLayer'
        # it doesn't say *which* module
        raise AttributeError('module %r has no attribute %r'
                             % (module_name, module_layer_name))


def layer_sort_key(layer):
    """Compute sort key for layers.

    Based on the reverse MRO ordering in order to put layers with shared base
    layers next to each other.
    """
    seen = set()
    key = []

    # Note: we cannot reuse gather_layers() here because it uses a
    # different traversal order.
    binding = {}  # hack to avoid recursion -- for PY2

    def _gather(layer):
        seen.add(layer)
        # We make the simplifying assumption that the order of initialization
        # of base layers does not matter.  Given that, traversing the bases
        # in reverse order here keeps the ordering of layers in
        # testrunner-layers.rst the same as it was in older versions of
        # zope.testrunner, so let's use that.
        for base in layer.__bases__[::-1]:
            if base is not object and base not in seen:
                binding["_gather"](base)
        key.append(layer)

    binding["_gather"] = _gather
    _gather(layer)
    try:
        return tuple(name_from_layer(ly) for ly in key if ly != UnitTests)
    finally:
        binding.clear()  # break reference cycle


def order_by_bases(layers):
    """Order the layers from least to most specific (bottom to top).

    Puts unit tests first.  Groups layers with common base layers together.
    Sorts the rest alphabetically.  Removes duplicates.
    """
    layers = sorted(layers, key=layer_sort_key, reverse=True)
    gathered = []
    for layer in layers:
        gather_layers(layer, gathered)
    gathered.reverse()
    seen = {}
    result = []
    for layer in gathered:
        if layer not in seen:
            seen[layer] = 1
            if layer in layers:
                result.append(layer)
    return result


def gather_layers(layer, result):
    if layer is not object:
        result.append(layer)
    for b in layer.__bases__:
        gather_layers(b, result)


class FakeInputContinueGenerator:

    def readline(self):
        print('c\n')
        print('*' * 70)
        print("Can't use pdb.set_trace when running a layer"
              " as a subprocess!")
        print('*' * 70)
        print()
        return 'c\n'

    def close(self):
        pass


def repr_lines(obj, max_width=75, max_lines=5):
    """represent *obj* by a sequence of text lines.

    Use at most *max_lines*, each with at most *max_width* chars.
    """
    try:
        oi = pprint.pformat(obj)
    except Exception:
        # unprintable
        oi = f"{obj.__class__} instance at 0x{id(obj):x}"
    # limit
    cmps = oi.split("\n", max_lines)
    if len(cmps) > max_lines:
        cmps[-1] = "..."
    for i, li in enumerate(cmps):
        if len(li) > max_width:
            cmps[i] = li[:max_width - 3] + "..."
    return cmps
