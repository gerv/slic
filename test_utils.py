# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import os
import re
from nose.tools import *
import utils

class TestBinaryDetection():
    def test_is_binary(self):
        dir = os.path.join("test_data", "is_binary")
        # For each line
        for line in open(os.path.join(dir, "index.csv")):
            line = line.strip()
            if line == '' or re.match("Header", line):
                continue

            yield self.check_is_binary, line, dir

    def check_is_binary(self, line, dir):
            # Split "CSV" file into parts using naive parsing
            filename, answer = line.split(',')

            # Do identification
            result = utils.is_binary(os.path.join(dir, filename))

            assert_equal(result,
                         bool(int(answer)),
                         msg="'%s' is wrongly classified" % filename)

class TestCollapse():
    def test_collapse(self):
        result = utils.collapse("   ")
        assert_equal(result, "")

        result = utils.collapse("  foo")
        assert_equal(result, "foo")

        result = utils.collapse("foo   ")
        assert_equal(result, "foo")

        result = utils.collapse("  foo    bar  ")
        assert_equal(result, "foo bar")

        result = utils.collapse("foo\t\nbar\r")
        assert_equal(result, "foo bar")
