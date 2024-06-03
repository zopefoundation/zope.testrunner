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
import sys


PY313 = sys.version_info[:2] >= (3, 13)


def make_sure_gc_threshold_is_701_11_9():
    pass


make_sure_gc_threshold_is_701_11_9.__doc__ = """\
>>> import gc
>>> gc.get_threshold()
(701, 11, %d)
""" % (0 if PY313 else 9)


def test_suite():
    return doctest.DocTestSuite()
