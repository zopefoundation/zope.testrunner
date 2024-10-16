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
"""Thread support beyond ``threading``.

``threading.enumerate`` may or may not know threads
started with ``_thread.start_new_thread``. If it knows them,
it does not know when they stop.
If ``sys._current_frames`` is available, use this to
reliable determine the currently running threads.
"""
import sys
import threading


current_frames = getattr(sys, "_current_frames", None)

if current_frames is None:  # pragma: no cover
    enumerate = threading.enumerate
else:
    def enumerate():
        """return sequence of proxies for the currently running threads."""
        running = set(current_frames())
        th_known = {t.ident: t for t in threading.enumerate()}
        return [ThreadProxy(th_known[i] if i in th_known else DummyThread(i))
                for i in running]


class ThreadProxy:
    """auxiliary class to provide ident based ``__eq__``."""

    def __init__(self, thread):
        self.thread = thread

    def __eq__(self, other):
        return self.thread.ident == other.thread.ident

    def __repr__(self):
        return repr(self.thread)

    def __getattr__(self, k):
        return getattr(self.thread, k)


class DummyThread:
    """auxiliary to represent a thread unknown to ``threading``."""

    def __init__(self, ident):
        self.ident = ident
        self.name = "Dummy-%s" % ident

    def __repr__(self):
        return "DummyThread %s, started, daemon" % self.ident

    def is_alive(self):
        return True
