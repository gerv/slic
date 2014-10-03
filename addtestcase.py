#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##############################################################################

import os
import sys
import argparse
import subprocess
import json
import shutil

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

# Find absolute path to passed-in file
parser = argparse.ArgumentParser(description='Add one or more files to the relic testcase set.')
parser.add_argument('files', metavar='<file>', nargs='+',
                    help='a file for the testcase set')

args = parser.parse_args()

id_dir = os.path.join(get_script_path(), "test_data", "identification")

for filename in args.files:
    filename = os.path.realpath(filename)
    basename = os.path.basename(filename)
    destname = os.path.join(id_dir, basename)

    if os.path.isfile(destname):
        print "*** File " + destname + " already exists - not adding."
        continue

    print "Adding file " + filename + "..."
    
    # Run relic on it and capture result
    relic = os.path.join(get_script_path(), "relic")
    output = subprocess.check_output([relic, "-f", "-g", "-m", filename])
    result = json.loads(output)
    
    # Strip out level of indirection with license hash
    result = result[result.keys()[0]]
    
    tag = result['tag']
    length = 0
    if 'text' in result:
        length = len(result['text'])
    
    # Copy file to test directory
    shutil.copy(filename, id_dir)
    
    # Add entry to index.csv
    index_name = os.path.join(id_dir, "index.csv") 
    with open(index_name, "a") as index_fh:
        index_fh.write(",".join([basename, tag, str(length)]))
        index_fh.write("\n")

