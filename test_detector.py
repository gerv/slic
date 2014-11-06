# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import detector
import config
import unittest
import os
from license_data import license_data

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


    def test_extract_copyrights_and_license(self):
        dtr = detector.Detector(license_data)
        
        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block0, 'MPL-2.0')
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block1, 'MPL-2.0')
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs", "Copyright (C) 2009-2012  George Jones"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = \
                   dtr.extract_copyrights_and_license(self.block2, 'MPL-2.0')
        self.assertEqual(license, self.mpl2)

        
    def test_id_license(self):
        dtr = detector.Detector(license_data)
        
        tags = dtr.id_license(self.mpl2)
        self.assertEqual(tags[0], 'MPL-2.0')
        self.assertEqual(len(tags), 1)

    def test_compilation(self):
        # Missing key
        data = { '': { 'start': '', 'match': '', 'end': ''} }
        self.assertRaises(Exception, detector.Detector, data)

        # Duplicate key
        data = { 'foo': { 'start': '', 'match': '', 'end': '', 'subs': {\
                  'foo': { 'start': '', 'match': '', 'end': ''} } } }
        self.assertRaises(Exception, detector.Detector, data)

        # Underscore start in orig data
        data = { '_foo': { 'start': '', 'match': '', 'end': ''} }
        self.assertRaises(Exception, detector.Detector, data)
        
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
        self.assertEqual(dtr._license_data['MPL-1.1']['start'], \
                         r"The contents of this (file|package) are subject to the")


if __name__ == '__main__':
    unittest.main()
