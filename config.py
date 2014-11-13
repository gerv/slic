###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Configuration interface for slic. Uses ini files to define much of how
# slic and the detector work.
###############################################################################

import re
import os
import sys
import ConfigParser

import logging
logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

config = ConfigParser.ConfigParser(allow_no_value=True)
# Make it case-sensitive
config.optionxform = str

# This is sadly necessary for nosetests to pass; an ini file is required
config.read(['/usr/src/relic/slic.ini'])

def read(files):
    config.read(files)

def get_option(section, option):
    retval = None
    try:
        retval = config.get(section, option)
    except ConfigParser.NoOptionError:
        pass

    return retval

def has_option(section, option):
    return config.has_option(section, option)

# Returns comment delimiters for this filename, or None if we can't work it
# out
def get_delims(path):
    delims = None

    # There are some extensions which need stripping off to show the 'real'
    # extension
    filename = os.path.basename(path)
    noext, ext = os.path.splitext(filename)

    log.debug("noext: %s; Ext: %s" % (noext, ext))
    
    # Strip extensions which hide the real extension. E.g. "foo.bar.in" is
    # generally a precursor for file "foo.bar" and uses the same comment char.
    # So we remove the .in and then look again.
    if config.has_option("strip_exts", ext):
        filename = noext
        noext, ext = os.path.splitext(noext)

    log.debug("Filename: %s; Ext: %s" % (filename, ext))
    
    # First see if we have a special setting for this filename
    delims = get_option("filename_to_comment", filename)

    # Then try the file extension
    if delims is None:
        delims = get_option("ext_to_comment", ext)

    # Then try the basename
    if delims is None:
        delims = get_option("noextname_to_comment", noext)
    
    log.debug("Delims: %r" % delims)
    
    if delims is None:
        # try to use the shebang line, if any
        fin = open(path, 'r')
        firstline = fin.readline()
        fin.close()
        # Almost all #! file types use # as the comment character
        if firstline.startswith("#!"):
            if re.search("env node", firstline):
                delims = '/*, *, */'
            else:
                delims = '#'
    
    if delims is not None:
        # Convert from string to Python structure - split on "|", then on ","
        # A delim is an array of exactly 1 or 3 members
        delims = re.split(r'\s*\|\s*', delims)
        for index, delim in enumerate(delims):
            if re.search(',', delim):
                delims[index] = re.split(r',\s*', delim)
                if len(delims[index]) != 3:
                    print "Error in delims for file %s" % filename
                    sys.exit(2)
            # "No delimiter" is encoded by special value ""
            elif delim == '""':
                delims[index] = ['']
            else:
                delims[index] = [delim]

    log.debug("Delims: %r" % delims)
    
    return delims


def _get_ext(filename):
    splitname = os.path.splitext(filename)
    
    # Strip extensions which hide the real extension. E.g. "foo.bar.in" is
    # generally a precursor for file "foo.bar" and uses the same comment char.
    # So we remove the .in and then look again.
    if config.has_option("strip_exts", splitname[1]):
        splitname = os.path.splitext(splitname[0])

    return splitname[1]
