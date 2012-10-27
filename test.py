import licblock
import config
import unittest

class TestStringMunging(unittest.TestCase):
    def test_collapse_whitespace(self):
        result = licblock.collapse_whitespace("   ")
        self.assertEqual(result, "")

        result = licblock.collapse_whitespace("  foo")
        self.assertEqual(result, "foo")

        result = licblock.collapse_whitespace("foo   ")
        self.assertEqual(result, "foo")

        result = licblock.collapse_whitespace("  foo    bar  ")
        self.assertEqual(result, "foo bar")

        result = licblock.collapse_whitespace("foo\t\nbar\r")
        self.assertEqual(result, "foo bar")

    def test_canonicalize_comment(self):
        result = licblock.canonicalize_comment(["Wibble"])
        self.assertEqual(result, "Wibble")
        
        result = licblock.canonicalize_comment(["  Wibble ", " Fish  ", "R "])
        self.assertEqual(result, "Wibble Fish R")

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

    
class TestLicenseMunging(unittest.TestCase):
    def setUp(self):
        self.mpl2 = """\
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
""".splitlines()

        self.block0 = """
Copyright (C) 2010 Fred Bloggs
  
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
""".splitlines()

        self.block1 = """\
Copyright (C) 2010 Fred Bloggs
Copyright (C) 2009-2012  George Jones

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.""".splitlines()

        self.block2 = """\
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

""".splitlines()


    def test_extract_copyrights(self):
        (copyrights, license) = licblock.extract_copyrights(self.block0)
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = licblock.extract_copyrights(self.block1)
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs", "Copyright (C) 2009-2012  George Jones"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = licblock.extract_copyrights(self.block2)
        self.assertEqual(license, self.mpl2)

        
    def test_identify_license(self):
        self.assertTrue(licblock.identify_license(self.mpl2))


class TestCommentFinding(unittest.TestCase):
    def setUp(self):
        self.block0 = """\
# This is a comment
this is not
# This is, and it
# runs over multiple lines
var x = 0
# Another one
# this time over
# 3 lines, and ending on the last line
""".splitlines()

        self.block1 = """\
This is not a comment
/* Start of block comment, one line */
/* Immediately following comment
 * Over multiple lines */

/* Another comment
* This time with
 * the terminator on its own line
*/
And this is not a comment
/* This is a comment which extends to the
 * final line */
""".splitlines()

        self.block2 = """\
#    This is a comment with multiple spaces before the text

    #    This is a comment with spaces before and after the comment char

\t# This is a comment starting with a tab

## Here's one where the comment char is doubled

# This is a line comment exactly 1 line from the end

""".splitlines()

    def test_find_next_comment(self):
        delims = ['#']
        end_line = 0
        results = [(0, 1), (2, 4), (5, 8), (-1, None)]
        
        for result1, result2 in results:
            (start_line, end_line) = licblock.find_next_comment(end_line, self.block0, delims)
            self.assertEqual(start_line, result1)
            self.assertEqual(end_line, result2)

        delims = ['/*', '*', '*/']
        end_line = 0
        results = [(1, 2), (2, 4), (5, 9), (10, 12), (-1, None)]
        
        for result1, result2 in results:
            (start_line, end_line) = licblock.find_next_comment(end_line, self.block1, delims)
            self.assertEqual(start_line, result1)
            self.assertEqual(end_line, result2)

        delims = ['#']
        end_line = 0
        results = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (-1, None)]
        
        for result1, result2 in results:
            (start_line, end_line) = licblock.find_next_comment(end_line, self.block2, delims)
            self.assertEqual(start_line, result1)
            self.assertEqual(end_line, result2)


class TestGetLicenseBlock(unittest.TestCase):
    def test_get_license_block(self):
        licenses = {}
        lic_hash = "291fc3e3c632e671df470cbefbfbe07c"
        filename = "test_data/main.cc"
        
        licblock.get_license_block(filename, licenses)
        self.assertIn(lic_hash, licenses)
        self.assertIn('text', licenses[lic_hash])
        text = licenses[lic_hash]['text']
        self.assertRegexpMatches(text[0], '^ This is part of')
        self.assertIn('copyrights', licenses[lic_hash])
        
        copyrights = licenses[lic_hash]['copyrights']
        copy_hash = "157d5ef2a199fa205a4ba57f919a0338"
        self.assertIn(copy_hash, copyrights)
        self.assertEqual(copyrights[copy_hash], "Copyright \xc2\xa9 2007,2008,2009 Red Hat, Inc.")
        
if __name__ == '__main__':
    unittest.main()
