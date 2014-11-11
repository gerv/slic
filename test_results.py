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

from results import Results

class TestLicenseMunging():
    def setup(self):
        pass

    def test__find_details(self):
        data = """
[ {
    "files": [ "foo.html" ], 
    "text": [
      "Redistribution and use in source and binary forms, with or without", 
      "modification, are permitted provided that the following conditions", 
      "are met:" ], 
    "tag": "BSD-4-Clause", 
    "copyrights": []
  },
]"""
        res = Results(data)
        

if __name__ == '__main__':
    nose.main()
