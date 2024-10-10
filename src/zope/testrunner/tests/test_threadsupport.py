##############################################################################
#
# Copyright (c) 2022 Zope Foundation and Contributors.
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
from _thread import start_new_thread
from threading import Lock
from threading import Thread
from time import sleep
from unittest import TestCase
from unittest import skipUnless

from ..threadsupport import current_frames
from ..threadsupport import enumerate


class ThreadMixin:
    """test thread."""

    def __init__(self):
        self.lock = Lock()
        self.stopped = False

    def run(self):
        with self.lock:
            pass
        self.stopped = True


class ThrThread(ThreadMixin, Thread):
    """``threading.Thread`` thread."""

    def __init__(self, name):
        Thread.__init__(self, name=name)
        ThreadMixin.__init__(self)


class DummyThread(ThreadMixin):
    def start(self):
        start_new_thread(self.run, ())


class Tests(TestCase):
    def setUp(self):
        self._threads = []
        self._prethreads = enumerate()

    def tearDown(self):
        for t in self._threads:
            if not t.stopped:
                t.lock.release()
                sleep(0.01)

    def _mk_thread(self, name=None):
        """create a new thread and start it.

        Use a full thread if *name*; otherwise a dummy thread.
        """
        t = ThrThread(name) if name else DummyThread()
        t.lock.acquire()
        t.start()
        self._threads.append(t)
        sleep(0.01)
        return t

    def alive(self):
        """alive threads not in ``_prethreads``."""
        return [p for p in enumerate()
                if p.is_alive() and p not in self._prethreads]

    def test_thr_proxy(self):
        self.check_proxy("Test ThrThread")

    @skipUnless(current_frames, "no `current_frames`")
    def test_dummy_proxy(self):
        self.check_proxy()

    def check_proxy(self, name=None):
        t = self._mk_thread(name)
        prs = self.alive()
        self.assertEqual(len(prs), 1)
        pr = prs[0]
        self.assertTrue(pr.is_alive())
        if name is None:
            self.assertTrue(pr.name.startswith("Dummy-"))
            self.assertIn("DummyThread", repr(pr))
        else:
            self.assertEqual(pr.name, t.name)
            self.assertEqual(repr(pr), repr(t))

    def test_thr_new_thread(self):
        self.check_new_thread("Test ThrThread")

    @skipUnless(current_frames, "no `current_frames`")
    def test_dummy_new_thread(self):
        self.check_new_thread()

    def check_new_thread(self, name=None):
        self._mk_thread(name and (name + "-1"))
        threads = self.alive()
        self._mk_thread(name and (name + "-2"))
        new_threads = [p for p in self.alive() if p not in threads]
        self.assertEqual(len(new_threads), 1)

    def test_thr_stopped(self):
        self.check_stopped("Test ThrThread")

    @skipUnless(current_frames, "no `current_frames`")
    def test_dummy_stopped(self):
        self.check_stopped()

    def check_stopped(self, name=None):
        t = self._mk_thread(name)
        t.lock.release()
        sleep(0.01)
        self.assertEqual(self.alive(), [])
