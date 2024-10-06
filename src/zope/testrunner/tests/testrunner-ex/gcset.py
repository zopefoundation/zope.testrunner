##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
import doctest
import gc


# for some early 3.13 versions, the third threshold has been
# a constant 0; this was changed again for newer versions
_thresholds = gc.get_threshold()
gc.set_threshold(10, 10, 10)
ZERO_THR3 = gc.get_threshold()[2] == 0
gc.set_threshold(*_thresholds)


def make_sure_gc_threshold_is_701_11_9():
    pass


make_sure_gc_threshold_is_701_11_9.__doc__ = """\
>>> import gc
>>> gc.get_threshold()
(701, 11, %d)
""" % (0 if ZERO_THR3 else 9)


def test_suite():
    return doctest.DocTestSuite()
