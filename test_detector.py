# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import config
import os
import re

from nose.tools import *
from license_data import license_data

import detector

class TestLicenseMunging():
    def setup(self):
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


    def test__find_details(self):
        dtr = detector.Detector(license_data, {'details': True})
        
        (copyrights, license) = \
                   dtr._find_details(self.block0, 'MPL-2.0')
        assert_equal(copyrights, ["Copyright (C) 2010 Fred Bloggs"])
        assert_equal(license, self.mpl2)

        (copyrights, license) = \
                   dtr._find_details(self.block1, 'MPL-2.0')
        assert_equal(copyrights, ["Copyright (C) 2010 Fred Bloggs", "Copyright (C) 2009-2012  George Jones"])
        assert_equal(license, self.mpl2)

        (copyrights, license) = \
                   dtr._find_details(self.block2, 'MPL-2.0')
        assert_equal(license, self.mpl2)

        
    def test__find_license(self):
        dtr = detector.Detector(license_data)
        
        tags = dtr._find_license(self.mpl2)
        assert_equal(tags[0], 'MPL-2.0')
        assert_equal(len(tags), 1)

    def test_compilation(self):
        # Missing key
        data = { '': { 'start': '', 'match': '', 'end': ''} }
        assert_raises(Exception, detector.Detector, data)

        # Duplicate key
        data = { 'foo': { 'start': '', 'match': '', 'end': '', 'subs': {\
                  'foo': { 'start': '', 'match': '', 'end': ''} } } }
        assert_raises(Exception, detector.Detector, data)

        # Underscore start in orig data
        data = { '_foo': { 'start': '', 'match': '', 'end': ''} }
        assert_raises(Exception, detector.Detector, data)
        
        data1 = {
            'MPL-1.1': {
                'start':  r"The contents of this (file|package) are subject to the",
                'match':  r"subject to the Mozilla Public License Version 1.1",
                'end':    r"Contributor|All Rights Reserved|Initial Developer",
                'subs': {
                    'MPL-1.1|GPL-2.0|LGPL-2.1': { # Mozilla
                        'start':  r"The contents of this (file|package) are subject to the",
                        'match':  r"either the GNU General",
                        'end':    r"terms of any one of the MPL, the GPL or the LGPL"
                    },         
                }
            },
        };
        
        dtr = detector.Detector(license_data)        
        assert_equal(dtr._license_data['MPL-1.1']['start'], \
                         r"The contents of this (file|package) are subject to the")


    def test_identification(self):
        dtr = detector.Detector(license_data, {'details': True})
        dir = os.path.join("test_data", "identification")
        # For each line
        for line in open(os.path.join(dir, "index.csv")):
            line = line.strip()
            if line == '' or re.match("Header", line):
                continue

            yield self.check_identification, dtr, line, dir

    def check_identification(self, dtr, line, dir):
            # Split "CSV" file into parts using naive parsing
            filename, resultcount, tag, textlength, copyrightlength, tmp \
                                                              = line.split(',')

            # Do identification
            licenses = dtr.get_license_info(os.path.join(dir, filename))

            assert_equal(len(licenses), int(resultcount))
            
            licenses = sorted(licenses, key=lambda k: k['tag'])
            
            # Check metadata matches for first license found (alphabetical)
            result = licenses[0]
            assert_equal(result['tag'], tag)

            if 'text' in result:
                assert_equal(len(result['text']), int(textlength))
            else:
                assert_equal(0,
                             int(textlength),
                             msg="Text length zero for %s" % filename)

            if 'copyrights' in result:
                assert_equal(len(result['copyrights']), int(copyrightlength))
            else:
                assert_equal(0,
                             int(copyrightlength),
                             msg="Copyright length zero for %s" % filename)
                

class TestStringMunging():
    def test__strip_comment_chars_1(self):
        dtr = detector.Detector(license_data)
        result = dtr._strip_comment_chars(["# Foo", "# Bar"], ['#'])
        assert_equal(result, ["Foo", "Bar"])

        result = dtr._strip_comment_chars(["# Foo", "  #  Bar"], ['#'])
        assert_equal(result, ["Foo", " Bar"])
        
    def test__strip_comment_chars_3(self):
        dtr = detector.Detector(license_data)
        result = dtr._strip_comment_chars(["/* Foo", "* Bar", "* Baz */"], ['/*', '*', '*/'])
        assert_equal(result, ["Foo", "Bar", "Baz"])
         
        result = dtr._strip_comment_chars(["/* Foo", "* Bar", "*/"], ['/*', '*', '*/'])
        assert_equal(result, ["Foo", "Bar", ""])

        result = dtr._strip_comment_chars(["/* **** Foo ****", "* Bar", "*/"], ['/*', '*', '*/'])
        assert_equal(result, ["**** Foo ****", "Bar", ""])


class TestCommentFinding():
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

    def test__find_next_comment(self):
        dtr = detector.Detector(license_data)
        
        for i in range(len(self.blocks)):
            delims =  self.blocks[i]['delims']
            results = self.blocks[i]['results']
            string =  self.blocks[i]['string'].splitlines()
            end_line = 0
        
            for result1, result2 in results:
                (start_line, end_line) = \
                      dtr._find_next_comment(end_line, string, delims)
                assert_equal(start_line, result1)
                assert_equal(end_line, result2)


if __name__ == '__main__':
    unittest.main()
