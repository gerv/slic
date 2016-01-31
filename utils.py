#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import re

import logging
logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

# Bytes which can be a part of valid text chars in 4-byte UTF-8.
# http://en.wikipedia.org/wiki/UTF-8#Codepage_layout

_textchars = bytearray([7,8,9,10,12,13,27]) + \
             bytearray(range(0x20, 0xC0)) + \
             bytearray(range(0xC2, 0xF5))

_is_binary_string = lambda bytes: bool(bytes.translate(None, _textchars))

# Stack Overflow 898669
def is_binary(filename):
    try:

        with open(filename, 'rb') as binaryfile:
            data = binaryfile.read(1024)
            if not data:
                # 0-byte file. If a file is 0 bytes, can it truly be said to be
                # binary or not binary? Deep. Still, we should ignore it.
                return True
            else:
                return _is_binary_string(data)
    except IOError:
        log.warning("Can't open file '%s' to see if it's binary", filename)
        return True

def collapse(line):
    # Collapse whitespace
    return re.sub("\s+", " ", line).strip()
