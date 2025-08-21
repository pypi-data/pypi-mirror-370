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
from __future__ import unicode_literals
$Id:$
"""
from __future__ import unicode_literals
from __future__ import absolute_import
__docformat__ = "reStructuredText"

import zope.interface


class IParserField(zope.interface.Interface):
    """Parser field holds a key and value given from a POST request."""

    name = zope.interface.Attribute("Field name")

    value = zope.interface.Attribute("Field value")


class ISimpleField(IParserField):
    """Simple field used in parser for none file upload data storage."""


class IMultiPartField(IParserField):
    """Multi part field used in parser for file upload data storage."""

    def addPart(self, part):
        """Add part to the list"""

    def readMulti(self, environ):
        """Read a part that is itself multipart."""

    def readSingle(self):
        """Read an atomic part."""

    def readBinary(self):
        """Read binary data."""

    def readLines(self):
        """Read lines until EOF or outerboundary.
        
        Start with a StringIO, later we move the content to a tmp file if the
        data will become to big.
        """

    def readLinesToEOF(self):
        """Read lines until EOF."""

    def readLinesToOuterboundary(self):
        """Read lines until outerboundary."""

    def skipLines(self):
        """Skip lines until outer boundary is defined."""

    def makeTMPFile(self):
        """Returns a temporary file in write mode."""
