##############################################################################
#
# Copyright (c) 2024 Zope Foundation and Contributors.
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
import unittest


class TestSomething(unittest.TestCase):

    def test_subTest(self):
        with self.subTest("fail 1"):
            self.assertEqual(0, 1)
        with self.subTest("success"):
            self.assertEqual(0, 0)
        with self.subTest("fail 2"):
            self.assertEqual(0, 1)
