##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import doctest
import re
import unittest

from z3c.testing import InterfaceBaseTest
from zope.testing import renormalizing

from p01.cgi import interfaces
from p01.cgi import parser

checker = renormalizing.RENormalizing([
    (re.compile('\r\n'), '\n'),
    ])


class SimpleFieldTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISimpleField

    def getTestClass(self):
        return parser.SimpleField

    def getTestPos(self):
        return ('foo', 'bar')


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        unittest.makeSuite(SimpleFieldTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
