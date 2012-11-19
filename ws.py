###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
import re

def collapse(line):
    # Collapse whitespace
    line = re.sub("\s+", " ", line)

    # Strip leading and trailing whitespace
    line = re.sub("^\s", "", line)
    line = re.sub("\s$", "", line)
    
    return line
