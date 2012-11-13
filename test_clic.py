# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import clic
import unittest
import licblock

class TestStringMunging(unittest.TestCase):
    def test_collapse_whitespace(self):
        result = licblock.collapse_whitespace("   ")
        self.assertEqual(result, "")
