#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##############################################################################

# This script takes a file on the command line, runs relic on it to get the
# "answers" (which are presumably correct when you add it to the suite!) and
# then adds the file to the test suite with the answers.
#
# So when you update the code to cope with a particular file, call this
# script on it and hopefully it'll never break again without you noticing.

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
    sourcename = os.path.realpath(filename)
    basename   = os.path.basename(sourcename)
    destname   = os.path.join(id_dir, basename)
    
    print "Adding file %s..." % sourcename
    
    # Deal with possibly clashing names using subdirectories
    i = 1
    while os.path.isfile(destname):
        i = i + 1
        destname = os.path.join(id_dir, str(i), basename)

    if i >= 2:
        print "   (As %s)" % destname
        if not os.path.isdir(os.path.dirname(destname)):
            os.mkdir(os.path.dirname(destname))

    # Run relic on it and capture result
    relic = os.path.join(get_script_path(), "relic")
    output = subprocess.check_output([relic, "-f", "-g", "-m", sourcename])
    result = json.loads(output)

    if not result.keys():
        print "No data from relic"
        continue
    
    # Strip out level of indirection with license hash
    result = result[result.keys()[0]]
    
    tag = result['tag']
    
    textlength = "0"
    if 'text' in result:
        textlength = str(len(result['text']))

    copyrightlength = "0"
    if 'copyrights' in result:
        copyrightlength = str(len(result['copyrights']))

    # Copy file to test directory
    shutil.copy(sourcename, destname)
    
    # Add entry to index.csv
    indexname = os.path.join(id_dir, "index.csv") 
    with open(indexname, "a") as indexfh:
        indexfh.write(",".join([destname, tag, textlength, copyrightlength]))
        indexfh.write("\n")

