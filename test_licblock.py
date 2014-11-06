# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import config
import os
import re

import nose
from nose.tools import *

import licblock
from detector import Detector
from license_data import license_data

class TestGetLicenseInfo():
    def test_get_license_info(self):
        detector = Detector(license_data, {'details': True})
        licenses = {}
        lic_hash = "34eb9c77640f88975eff1c6ed92b6317"
        filename = "test_data/main.cc"
        
        licblock.get_license_info(filename, detector, licenses)
        assert_equal(len(licenses), 1)
        license = licenses.values()[0]
        assert_in('text', license)
        text = license['text']
        assert_regexp_matches(text[0], '^Permission is hereby granted')
        assert_in('copyrights', license)
        
        copyrights = license['copyrights']
        assert_equal(len(copyrights), 1)
        copyright = copyrights.keys()[0]
        assert_equal(copyright, u"Copyright \xa9 2007,2008,2009 Red Hat, Inc.")


if __name__ == '__main__':
    unittest.main()
