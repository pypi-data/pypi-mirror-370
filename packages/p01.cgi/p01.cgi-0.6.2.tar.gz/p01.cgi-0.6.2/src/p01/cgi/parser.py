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
__docformat__ = "reStructuredText"

import re
import os
import sys
import tempfile
from email import message_from_string
from io import BytesIO

import six
from six.moves import urllib
import zope.interface

from p01.cgi import interfaces

try:
    unicode
except Exception:
    unicode = str

PY3 = sys.version_info[0] == 3

# Debug configuration
DEBUG = True
DEBUG_OUT = sys.stderr

maxlen = 0
OVERSIZE_FIELD_CONTENT = 1000


@zope.interface.implementer(interfaces.ISimpleField)
class SimpleField:
    """Simple key value pair field."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<%s, %r = %r>" % (self.__class__.__name__, self.name, self.value)


def parseFormData(method, inputStream=None, headers=None, boundary="",
    environ=os.environ, tmpFileFactory=None, tmpFileFactoryArguments=None):
    if method in ('GET', 'HEAD'):
        qs = environ.get('QUERY_STRING')
        if qs:
            return [SimpleField(key, value) for key, value in parseQueryString(qs)]
        return None
    if method == 'POST':
        content_type = environ.get('CONTENT_TYPE', '')
        if content_type.startswith('multipart/'):
            fieldStorage = parseMultiParts(inputStream, headers, boundary,
                environ, tmpFileFactory, tmpFileFactoryArguments)
            return fieldStorage.list
        if content_type.startswith('application/x-www-form-urlencoded'):
            if headers is None:
                headers = {}
                headers['content-type'] = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
                if 'CONTENT_LENGTH' in environ:
                    headers['content-length'] = environ['CONTENT_LENGTH']
                elif 'HTTP_CONTENT_LENGTH' in environ:
                    headers['content-length'] = environ['HTTP_CONTENT_LENGTH']
            return parseUrlEncoded(inputStream, headers, environ)

    return None


def parseUrlEncoded(inputStream=None, headers=None, environ=os.environ):
    """Parse x-www-form-urlencoded form data and return a list of fields.
    No subparts or whatever supported"""
    # Robust content-length parsing
    clen = 0
    if headers:
        clen_raw = headers.get('content-length', 0)
        try:
            clen = int(clen_raw)
        except (TypeError, ValueError):
            # broken value -> -1: read to EOF
            clen = -1
    if clen == 0:
        return None
    raw_data = inputStream.read() if clen < 0 else inputStream.read(clen)
    try:
        qs = raw_data.decode('utf-8') if isinstance(raw_data, bytes) else raw_data
    except UnicodeDecodeError:
        qs = raw_data.decode('latin-1') if isinstance(raw_data, bytes) else raw_data
    if '\r\n' in qs:
        qs = qs.replace('\r\n', '&').replace('\n', '&')
        qs = '&'.join([p for p in qs.split('&') if p])
    fields = []
    for pair in qs.split('&'):
        if not pair:
            continue
        parts = pair.split('=', 1)
        key = urllib.parse.unquote(parts[0].replace('+', ' ')).strip()
        value = urllib.parse.unquote(parts[1].replace('+', ' ')).strip() if len(parts) > 1 else ''
        if value.startswith('\r\n'):
            value = value[2:].strip()
        elif value.endswith('\r\n'):
            value = value[:-2].strip()
        fields.append(SimpleField(key, value))
    return fields


def parseQueryString(qs):
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for kv in pairs:
        if not kv:
            continue
        nv = kv.split('=', 1)
        if len(nv) != 2:
            nv.append('')
        if len(nv[1]):
            name = urllib.parse.unquote(nv[0].replace('+', ' '))
            value = urllib.parse.unquote(nv[1].replace('+', ' '))
            r.append((name, value))
    return r


def parseMultiParts(inputStream=None, headers=None, boundary="",
    environ=os.environ, tmpFileFactory=None, tmpFileFactoryArguments=None):
    """Parse multipart form data and return a list of fields.
    Or called for a contained part (where content-disposition is ``form-data``
    Or called for a separator part that gets thrown away"""

    # Keep the original 3-in-1 behavior; normalization only.
    fieldStorage = MultiPartField(inputStream, boundary, tmpFileFactory,
        tmpFileFactoryArguments)

    # Prepare / normalize headers:
    # - If None: build from environ (as before)
    # - If Message or mapping: lowercase keys and coerce values to str
    if headers is None:
        norm_headers = {}
        norm_headers['content-type'] = environ.get('CONTENT_TYPE', 'text/plain')
        if 'CONTENT_LENGTH' in environ:
            norm_headers['content-length'] = environ['CONTENT_LENGTH']
        elif 'HTTP_CONTENT_LENGTH' in environ:
            norm_headers['content-length'] = environ['HTTP_CONTENT_LENGTH']
    else:
        # Do not fall back to environ for inner parts. An empty mapping {} means:
        # "no headers for this inner part" (e.g., preamble/separator).
        items = headers.items() if hasattr(headers, "items") else []
        norm_headers = {}
        for k, v in items:
            k = (k.decode('latin-1') if isinstance(k, bytes) else str(k)).lower()
            if isinstance(v, bytes):
                try:
                    v = v.decode('latin-1')
                except Exception:
                    v = v.decode('utf-8', 'replace')
            else:
                v = str(v)
            norm_headers[k] = v

    fieldStorage.headers = norm_headers

    # content-disposition
    cdisp, pdict = "", {}
    if 'content-disposition' in fieldStorage.headers:
        cdisp, pdict = parseHeader(fieldStorage.headers['content-disposition'])
    fieldStorage.disposition = cdisp
    fieldStorage.disposition_options = pdict

    if 'name' in pdict:
        fieldStorage.name = pdict['name']

    if 'filename' in pdict:
        fieldStorage.filename = pdict['filename'] or None

    # content-type
    ctype, pdict = "text/plain", {}
    if 'content-type' in fieldStorage.headers:
        ctype, pdict = parseHeader(fieldStorage.headers['content-type'])
    fieldStorage.type = ctype
    fieldStorage.type_options = pdict
    fieldStorage.innerboundary = pdict.get('boundary', "")

    # robust content-length
    clen = -1
    if 'content-length' in fieldStorage.headers:
        raw_len = fieldStorage.headers['content-length']
        try:
            clen = int(raw_len)
        except (TypeError, ValueError):
            clen = -1
        if maxlen and clen > maxlen:
            raise ValueError('Maximum content length exceeded')
    fieldStorage.length = clen

    if ctype.startswith('multipart/'):
        fieldStorage.readMulti(environ)
    else:
        fieldStorage.readSingle()

    return fieldStorage


def validBoundary(s):
    return re.match("^[ -~]{0,200}[!-~]$", s)


def parseHeader(line):
    """Returns the main content-type and a dictionary of options."""
    if isinstance(line, bytes):
        line = line.decode('latin-1')
    plist = [x.strip() for x in line.split(';')]
    key = plist.pop(0).lower()
    pdict = {}
    for p in plist:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i + 1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    return key, pdict


@zope.interface.implementer(interfaces.IMultiPartField)
class MultiPartField:

    def __init__(self, inputStream=None, boundary="", tmpFileFactory=None,
        tmpFileFactoryArguments=None):
        """MultiPartField used for multipart content."""
        self.inputStream = inputStream
        self.outerboundary = boundary
        self.innerboundary = ""
        self.bufsize = 8 * 1024
        self.length = -1
        self.done = 0
        self.name = None
        self.filename = None
        self.list = None
        self.file = None
        if tmpFileFactory is None:
            self.tmpFileFactory = tempfile.TemporaryFile
        else:
            self.tmpFileFactory = tmpFileFactory
        self.tmpFileFactoryArguments = tmpFileFactoryArguments

    @property
    def value(self):
        if self.file and self.filename is None:
            # for non-upload atomic parts, return file content as value
            self.file.seek(0)
            value = self.file.read()
            if isinstance(value, bytes):
                value = value.decode('latin-1')
            self.file.seek(0)
            return value
        elif self.list is not None:
            return self.list
        return None

    def addPart(self, part):
        if self.list is None:
            self.list = []
        self.list.append(part)

    def readMulti(self, environ):
        ib = self.innerboundary
        if not validBoundary(ib):
            raise ValueError('Invalid boundary in multipart form: %r' % (ib,))
        self.list = []

        # consume possible preamble up to first boundary
        preamble = parseMultiParts(self.inputStream, {}, ib, environ,
            self.tmpFileFactory, self.tmpFileFactoryArguments)

        part = preamble
        while not part.done:
            # read header lines for the next part
            header_lines = []
            while True:
                line = self.inputStream.readline(1 << 16)
                if not line:
                    self.done = -1
                    break
                if line in (b'\r\n', b'\n'):
                    break
                header_lines.append(line.decode('latin-1'))
            headers = message_from_string(''.join(header_lines))

            # parse the next part body up to next boundary
            part = parseMultiParts(self.inputStream, headers, ib, environ,
                self.tmpFileFactory, self.tmpFileFactoryArguments)
            self.addPart(part)

        # preamble was not added to self.list -> close it explicitly
        try:
            preamble.close()
        except Exception:
            pass

        self.skipLines()

    def readSingle(self):
        """Read an atomic part."""
        if self.length >= 0:
            self.readBinary()
            self.skipLines()
        else:
            self.readLines()
        if self.file:
            self.file.seek(0)

    def readBinary(self):
        """Read binary data."""
        self.file = self.makeTMPFile()
        todo = self.length
        if todo >= 0:
            while todo > 0:
                data = self.inputStream.read(min(todo, self.bufsize))
                if not data:
                    self.done = -1
                    break
                self.file.write(data)
                todo = todo - len(data)

    def readLines(self):
        """Read lines until EOF or outerboundary."""
        if self.filename is not None:
            # file upload -> use tmpFileFactory directly
            self.file = self.makeTMPFile()
            self.__file = None
        else:
            # non-file: start with BytesIO; if value grows, spill to tmp file
            self.file = self.__file = BytesIO()
        if self.outerboundary:
            self.readLinesToOuterboundary()
        else:
            self.readLinesToEOF()

    def __write(self, line):
        if self.__file is not None:
            if self.__file.tell() + len(line) > OVERSIZE_FIELD_CONTENT:
                # spill to tmp file if too large
                self.file = self.makeTMPFile()
                self.file.write(self.__file.getvalue())
                self.__file = None

        # always write bytes
        if isinstance(line, unicode):
            line = line.encode('utf-8')
        elif not isinstance(line, bytes):
            line = str(line).encode('utf-8')

        self.file.write(line)

    def readLinesToEOF(self):
        while 1:
            line = self.inputStream.readline(1 << 16)
            if not line:
                self.done = -1
                break
            self.__write(line)

    def readLinesToOuterboundary(self):
        next = "--" + self.outerboundary
        last = next + "--"
        delim = b""
        last_line_lfend = True
        value_buffer = []

        while 1:
            line = self.inputStream.readline(1 << 16)
            if not line:
                self.done = -1
                break

            # boundary detection
            if line[:2] == b"--" and last_line_lfend:
                strippedline = line.strip()
                if strippedline == next.encode('latin-1'):
                    # reached next part boundary
                    break
                if strippedline == last.encode('latin-1'):
                    # reached final boundary
                    self.done = 1
                    break

            # normalize line endings and remember the original delimiter
            odelim = delim
            if line[-2:] == b"\r\n":
                delim = b"\r\n"
                line = line[:-2]
                last_line_lfend = True
            elif line[-1:] == b"\n":
                delim = b"\n"
                line = line[:-1]
                last_line_lfend = True
            else:
                delim = b""
                last_line_lfend = False

            # append previous delimiter + current line (keeps leading blank line)
            value_buffer.append(odelim + line)

        # HEADSUP: the last \n is a part of the boundary and all what we
        # write with __write get used as form value. So we have to skip the
        # line break separator as a part of the boundary
        # # ensure trailing newline of the last content line is preserved
        # if value_buffer and delim:
        #     value_buffer.append(delim)

        if value_buffer:
            self.__write(b"".join(value_buffer))

    def skipLines(self):
        if not self.outerboundary or self.done:
            return
        next = "--" + self.outerboundary
        last = next + "--"
        last_line_lfend = True
        while 1:
            line = self.inputStream.readline(1 << 16)
            if not line:
                self.done = -1
                break
            if line[:2] == b"--" and last_line_lfend:
                strippedline = line.strip()
                if strippedline == next.encode('latin-1'):
                    break
                if strippedline == last.encode('latin-1'):
                    self.done = 1
                    break
            last_line_lfend = line.endswith(b'\n')

    def makeTMPFile(self):
        if self.tmpFileFactoryArguments is not None:
            return self.tmpFileFactory(**self.tmpFileFactoryArguments)
        else:
            return self.tmpFileFactory()

    def close(self):
        """Close own file handles and children recursively."""
        # close children first
        if self.list:
            for p in self.list:
                try:
                    p.close()
                except Exception:
                    pass
        # close in-memory buffer (BytesIO) if present
        if getattr(self, "_MultiPartField__file", None) is not None:
            try:
                self.__file.close()
            except Exception:
                pass
            self.__file = None
        # close temp file if present
        if self.file is not None:
            try:
                self.file.close()
            except Exception:
                pass
            self.file = None

    # def __enter__(self):
    #     return self

    # def __exit__(self, exc_type, exc, tb):
    #     self.close()
    #     return False

    # def __del__(self):
    #     try:
    #         self.close()
    #     except Exception:
    #         # never raise from __del__
    #         pass

    def __repr__(self):
        if self.filename:
            return "<%s, %r: %r>" % (self.__class__.__name__, self.name, self.filename)
        else:
            return "<%s, %r>" % (self.__class__.__name__, self.name)
