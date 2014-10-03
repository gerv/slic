# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import licblock
import config
import unittest
import os
import re

class TestStringMunging(unittest.TestCase):
    def test_strip_comment_chars_1(self):
        result = licblock.strip_comment_chars(["# Foo", "# Bar"], ['#'])
        self.assertEqual(result, ["Foo", "Bar"])

        result = licblock.strip_comment_chars(["# Foo", "  #  Bar"], ['#'])
        self.assertEqual(result, ["Foo", " Bar"])
        
    def test_strip_comment_chars_3(self):
        result = licblock.strip_comment_chars(["/* Foo", "* Bar", "* Baz */"], ['/*', '*', '*/'])
        self.assertEqual(result, ["Foo", "Bar", "Baz"])
         
        result = licblock.strip_comment_chars(["/* Foo", "* Bar", "*/"], ['/*', '*', '*/'])
        self.assertEqual(result, ["Foo", "Bar", ""])

        result = licblock.strip_comment_chars(["/* **** Foo ****", "* Bar", "*/"], ['/*', '*', '*/'])
        self.assertEqual(result, ["**** Foo ****", "Bar", ""])


class TestCommentFinding(unittest.TestCase):
    def setUp(self):
        self.blocks = [{
            'delims':  ['#'],
            'results': [(0, 1), (2, 4), (5, 8), (-1, None)],
            'string':  """\
# This is a comment
this is not
# This is, and it
# runs over multiple lines
var x = 0
# Another one
# this time over
# 3 lines, and ending on the last line
"""},
        {
            'delims':  ['/*', '*', '*/'],
            'results': [(1, 2), (2, 4), (5, 9), (10, 12), (-1, None)],
            'string':  """\
This is not a comment
/* Start of block comment, one line */
/* Immediately following comment
 * Over multiple lines */
XXX
/* Another comment
* This time with
 * the terminator on its own line
*/
And this is not a comment
/* This is a comment which extends to the
 * final line */
"""},
        {
            'delims':  ['#'],
            'results': [(0, 1), (2, 3), (4, 5), (6, 7), (8, 11), (12, 13), (-1, None)],
            'string':  """\
#    This is a comment with multiple spaces before the text
XXX
    #    This is a comment with spaces before and after the comment char
XXX
\t# This is a comment starting with a tab
XXX
## Here's one where the comment char is doubled
XXX
# Part 1

# Part 2 - should be all one because blanks are ignored
XXX
# This is a line comment exactly 1 line from the end
XXX
"""},
        {
            'delims':  ['//'],
            'results': [(1, 2), (-1, None)],
            'string':  """\
/* Foo */
// Bar
/* Baz
 * Quux
 */
"""}
        ]

    def test_find_next_comment(self):
        for i in range(len(self.blocks)):
            delims =  self.blocks[i]['delims']
            results = self.blocks[i]['results']
            string =  self.blocks[i]['string'].splitlines()
            end_line = 0
        
            for result1, result2 in results:
                (start_line, end_line) = \
                      licblock.find_next_comment(end_line, string, delims)
                self.assertEqual(start_line, result1)
                self.assertEqual(end_line, result2)


class TestGetLicenseBlock(unittest.TestCase):
    def test_get_license_block(self):
        licenses = {}
        lic_hash = "34eb9c77640f88975eff1c6ed92b6317"
        filename = "test_data/main.cc"
        
        licblock.get_license_block(filename, licenses)
        self.assertEqual(len(licenses), 1)
        license = licenses.values()[0]
        self.assertIn('text', license)
        text = license['text']
        self.assertRegexpMatches(text[0], '^Permission is hereby granted')
        self.assertIn('copyrights', license)
        
        copyrights = license['copyrights']
        self.assertEqual(len(copyrights), 1)
        copyright = copyrights.keys()[0]
        self.assertEqual(copyright, u"Copyright \xa9 2007,2008,2009 Red Hat, Inc.")


class TestIdentification(unittest.TestCase):
    def test_identification(self):
        dir = os.path.join("test_data", "identification")
        # For each line
        for line in open(os.path.join(dir, "index.csv")):
            line = line.strip()
            if line == '':
                continue

            yield identify, line, dir

    def identify(line, dir):
        # Split into parts
        filename, tag, length = line.split(',')
        
        # Do identification
        licenses = {}
        licblock.get_license_block(os.path.join(dir, filename), licenses)
        
        # Check metadata matches
        result = licenses[licenses.keys()[0]]
        self.assertEqual(result['tag'], tag)
        if 'text' in result:
            self.assertEqual(len(result['text']), int(length))
        else:
            self.assertEqual(0, int(length))
                
if __name__ == '__main__':
    unittest.main()
