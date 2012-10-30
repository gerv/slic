import licblock
import config
import unittest
import os
import re

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
        self.assertEqual(result, "wibble")
        
        result = licblock.canonicalize_comment(["  Wibble ", " Fish  ", "R "])
        self.assertEqual(result, "wibble fish r")

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
XXX
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
""".splitlines()

        self.block3 = """\
/* Foo */
// Bar
/* Baz
 * Quux
 */
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
        results = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 11), (12, 13), (-1, None)]
        
        for result1, result2 in results:
            (start_line, end_line) = licblock.find_next_comment(end_line, self.block2, delims)
            self.assertEqual(start_line, result1)
            self.assertEqual(end_line, result2)

        delims = ['//']
        end_line = 0
        results = [(1, 2), (-1, None)]
        
        for result1, result2 in results:
            (start_line, end_line) = licblock.find_next_comment(end_line, self.block3, delims)
            self.assertEqual(start_line, result1)
            self.assertEqual(end_line, result2)


class TestGetLicenseBlock(unittest.TestCase):
    def test_get_license_block(self):
        licenses = {}
        lic_hash = "9dd63be914c2eff5b6938c3047a5bd66"
        filename = "test_data/main.cc"
        
        licblock.get_license_block(filename, licenses)
        self.assertIn(lic_hash, licenses)
        self.assertIn('text', licenses[lic_hash])
        text = licenses[lic_hash]['text']
        self.assertRegexpMatches(text[0], '^Permission is hereby granted')
        self.assertIn('copyrights', licenses[lic_hash])
        
        copyrights = licenses[lic_hash]['copyrights']
        copy_hash = "157d5ef2a199fa205a4ba57f919a0338"
        self.assertIn(copy_hash, copyrights)
        self.assertEqual(copyrights[copy_hash], "Copyright \xc2\xa9 2007,2008,2009 Red Hat, Inc.")

    # Test we correctly identify every test file in the test_data/licenses
    # directory (using the filename to give us the right answer).
    def test_get_license_block_2(self):
        dir = "test_data/licenses"
        for filename in os.listdir(dir):
            match = re.match("^\w+", filename)
            tag = match.group(0)
            
            licenses = {}
            licblock.get_license_block(os.path.join(dir, filename), licenses)

            self.assertEqual(licenses[licenses.keys()[0]]['tag'], tag)

        
if __name__ == '__main__':
    unittest.main()
