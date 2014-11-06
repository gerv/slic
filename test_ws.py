# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import nose
from nose.tools import *

import ws

class TestCollapse():
    def test_collapse(self):
        result = ws.collapse("   ")
        assert_equal(result, "")

        result = ws.collapse("  foo")
        assert_equal(result, "foo")

        result = ws.collapse("foo   ")
        assert_equal(result, "foo")

        result = ws.collapse("  foo    bar  ")
        assert_equal(result, "foo bar")

        result = ws.collapse("foo\t\nbar\r")
        assert_equal(result, "foo bar")


if __name__ == '__main__':
    nose.main()
