# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import nose
from nose.tools import *

import clic

class TestSplitYears():
    def test_split_years(self):
        assert_equal(clic._split_years(""), [])
        assert_equal(clic._split_years("1999"), [1999])
        assert_equal(clic._split_years("2000-2002"), [2000, 2001, 2002])
        assert_equal(clic._split_years("2000-2001, 2004"), [2000, 2001, 2004])
        assert_equal(clic._split_years("  2000 -   2001,  2004"), [2000, 2001, 2004])
        assert_equal(clic._split_years("1997-98"), [1997, 1998])


class TestJoinYears():
    def test_join_years(self):
        
        assert_equal(clic._join_years([]), "")
        assert_equal(clic._join_years([1999]), "1999")
        assert_equal(clic._join_years([1999, 2000]), "1999-2000")
        assert_equal(clic._join_years([1997, 1998, 1999, 2001]), "1997-1999, 2001")
        assert_equal(clic._join_years([1999, 2000, 2001, 2003, 2004]), "1999-2001, 2003-2004")
        assert_equal(clic._join_years([1999, 2001, 2003, 2006]), "1999, 2001, 2003, 2006")


if __name__ == '__main__':
    nose.main()
