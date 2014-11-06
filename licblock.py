# -*- coding: utf-8 -*-
##############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# A module for taking a file, extracting the comments, stripping off the
# comment characters, and using the license detector module to extract the
# copyright lines and license block.
##############################################################################
import re
import hashlib
import sys
import os.path
import config
import ws

import logging
logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

# "results" is an accumulating result parameter
def get_license_info(filename, detector, results):
    # It's possible to configure slic to look in a different place for the
    # license of a particular file (perhaps one it can't parse) 
    substitute = config.get_option("substitutes", filename)
    if substitute:
        if not os.path.isabs(substitute):
            script = os.path.realpath(sys.argv[0])
            substitute = os.path.join(os.path.dirname(script),
                                      "substitutes",
                                      substitute)
                                    
        licenses = detector.get_license_info(substitute)
    else:
        licenses = detector.get_license_info(filename)

    for license in licenses:
        lic_key = license['tag']
        # If this code mis-detects two licenses in exactly the same text, they
        # will get smooshed together here
        if 'text' in license and len(license['text']) > 0:
            lic_key = make_hash(license['text'])
        
        if lic_key in results:
            log.debug("Adding file %s to list" % filename)
            results[lic_key]['files'].append(filename)
            if 'copyrights' in license:
                results[lic_key]['copyrights'].update(license['copyrights'])
        else:
            log.debug("Starting new file list with file %s" % filename)
            license['files'] = [filename]
            results[lic_key] = license

    return


# Function to remove false positive differences from a thing or array and
# then return a unique identifier for it
def make_hash(thing):
    if type(thing) == str:
        thing = [thing]

    line = " ".join(thing)
    line = re.sub("[\*\.,\-\d]+", "", line)
    line = ws.collapse(line)

    line = line.encode('ascii', errors='ignore')
    line = line.lower()
    hash = hashlib.md5(line).hexdigest()

    return hash
