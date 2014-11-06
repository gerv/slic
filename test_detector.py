# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import config
import os

from nose.tools import *
from license_data import license_data

import detector
import licblock

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


    def test_extract_copyrights_and_license(self):
        dtr = detector.Detector(license_data)
        
        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block0, 'MPL-2.0')
        assert_equal(copyrights, ["Copyright (C) 2010 Fred Bloggs"])
        assert_equal(license, self.mpl2)

        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block1, 'MPL-2.0')
        assert_equal(copyrights, ["Copyright (C) 2010 Fred Bloggs", "Copyright (C) 2009-2012  George Jones"])
        assert_equal(license, self.mpl2)

        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block2, 'MPL-2.0')
        assert_equal(license, self.mpl2)

        
    def test_id_license(self):
        dtr = detector.Detector(license_data)
        
        tags = dtr.id_license(self.mpl2)
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
        dtr = detector.Detector(license_data)
        dir = os.path.join("test_data", "identification")
        # For each line
        for line in open(os.path.join(dir, "index.csv")):
            line = line.strip()
            if line == '':
                continue

            yield self.check_identification, dtr, line

    def check_identification(self, dtr, line):
            # Split "CSV" file into parts using naive parsing
            filename, tag, textlength, copyrightlength, tmp = line.split(',')

            # Do identification
            licenses = {}
            licblock.get_license_info(os.path.join(dir, filename), dtr, licenses)

            assert_true(len(licenses) > 0,
                            msg="At least one license found")
            
            licenses = sorted(licenses.values(), key=lambda k: k['tag'])
            
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
                

if __name__ == '__main__':
    unittest.main()
