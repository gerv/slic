# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import clic
import unittest

class TestSplitYears(unittest.TestCase):
    def test_split_years(self):
        self.assertEqual(clic._split_years(""), [])
        self.assertEqual(clic._split_years("1999"), [1999])
        self.assertEqual(clic._split_years("2000-2002"), [2000, 2001, 2002])
        self.assertEqual(clic._split_years("2000-2001, 2004"), [2000, 2001, 2004])
        self.assertEqual(clic._split_years("  2000 -   2001,  2004"), [2000, 2001, 2004])
        self.assertEqual(clic._split_years("1997-98"), [1997, 1998])


class TestJoinYears(unittest.TestCase):
    def test_join_years(self):
        
        self.assertEqual(clic._join_years([]), "")
        self.assertEqual(clic._join_years([1999]), "1999")
        self.assertEqual(clic._join_years([1999, 2000]), "1999-2000")
        self.assertEqual(clic._join_years([1997, 1998, 1999, 2001]), "1997-1999, 2001")
        self.assertEqual(clic._join_years([1999, 2000, 2001, 2003, 2004]), "1999-2001, 2003-2004")
        self.assertEqual(clic._join_years([1999, 2001, 2003, 2006]), "1999, 2001, 2003, 2006")


if __name__ == '__main__':
    unittest.main()
