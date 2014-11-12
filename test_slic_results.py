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

from slic_results import SlicResults

class TestSlicResults():
    def make_example(self):
        data = """{
    "BSD-4-Clause": [
    {
        "files": [ "foo.html" ], 
        "text": [
          "Redistribution and use in source and binary forms, with or without", 
          "modification, are permitted provided that the following conditions", 
          "are met:" ], 
        "tag": "BSD-4-Clause", 
        "copyrights": []
    },
    {
        "files": [ "quux.html", "baz.txt" ], 
        "text": [
          "Redistribution and use in source and binary forms, with or without", 
          "modification, are permitted provided that the following conditions", 
          "are met:" ], 
        "tag": "BSD-4-Clause", 
        "copyrights": ["Copyright (C) 2014 Fred Bloggs"]
    }],
      "GPL-2.0": [{
        "files": [ "bar.html" ], 
        "text": [ "" ], 
        "tag": "GPL-2.0", 
        "copyrights": []
      }]
}"""
        res = SlicResults()
        res.load_json(data)
        return res
                
    def test_creation(self):
        res = self.make_example()
        assert_equal(len(res), 2)
        assert_equal(res['BSD-4-Clause'][0]['files'][0], "foo.html")

    def test_unify(self):
        res = self.make_example()
        assert_equal(len(res['BSD-4-Clause']), 2)
        res.unify()
        assert_equal(len(res['BSD-4-Clause']), 1)
        data = res['BSD-4-Clause'][0]
        assert_equal(data['tag'], 'BSD-4-Clause')
        assert_equal(len(data['files']), 3)
        assert_equal(len(data['copyrights']), 1)

    def test_pop_by_re(self):
        res = self.make_example()
        bsd = res.pop_by_re("^BSD")
        assert_equal(len(bsd), 1)
        assert_equal(len(bsd['BSD-4-Clause']), 2)
        assert_equal(len(res), 1)
        assert_equal(len(res['GPL-2.0']), 1)

    def test_itervalues(self):
        res = self.make_example()
        values = [item for item in res.itervalues()]
        assert_equal(len(values), 3)
        values = [item for item in res.itervalues("^BSD")]
        assert_equal(len(values), 2)
        
if __name__ == '__main__':
    nose.main()
