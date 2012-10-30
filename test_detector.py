import detector
import config
import unittest
import os

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
        (copyrights, license) = \
                   detector.extract_copyrights_and_license(self.block0, 'mpl2')
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = \
                   detector.extract_copyrights_and_license(self.block1, 'mpl2')
        self.assertEqual(copyrights, ["Copyright (C) 2010 Fred Bloggs", "Copyright (C) 2009-2012  George Jones"])
        self.assertEqual(license, self.mpl2)

        (copyrights, license) = \
                   detector.extract_copyrights_and_license(self.block2, 'mpl2')
        self.assertEqual(license, self.mpl2)

        
    def test_id_license(self):
        self.assertEqual(detector.id_license(self.mpl2), 'mpl2')
        

if __name__ == '__main__':
    unittest.main()
