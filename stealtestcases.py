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
import random

with open("/usr/src/b2g/occurrences.json", "r") as fh:
    occurrences = json.load(fh)

    # Rejig data structure so top-level key is the tag instead of the license
    # text hash, and value is a list of the corresponding license objects
    bytag = {}

    for hash, occurrence in occurrences.items():
        tag = occurrence['tag']
        if tag in bytag:
            bytag[tag].append(occurrence)
        else:
            bytag[tag] = [occurrence]

    for tag, info in bytag.items():
        item = random.choice(info)
        filename = random.choice(item['files'])
        print "/usr/src/b2g/" + filename
