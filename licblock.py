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
import detector
import ws

import logging
logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

# This number is fairly performance-sensitive
MAX_SCAN_LINE = 400

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
                                    
        licenses = _get_licenses_for_file(substitute, detector)
    else:
        licenses = _get_licenses_for_file(filename, detector)

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


# Find the license or licenses in a file. Returns a list of license objects.
# The only guaranteed value in a license object is the 'tag', which may be
# 'none'.
def _get_licenses_for_file(filename, detector):    
    fin = open(filename, 'r')
    try:
        content = fin.read(MAX_SCAN_LINE * 80)
    finally:
        fin.close()

    try:
        content = content.decode('utf-8')
    except UnicodeDecodeError:
        content = content.decode('iso-8859-1')

    log.info("Processing: %s", filename)
    
    licenses = []

    # Get comment delimiter info for this file.
    comment_delim_sets = config.get_delims(filename)
    
    if not comment_delim_sets:
        # We can't handle this type of file
        log.warning("No comment delimiters for file %s" % filename)
        return licenses

    lines = content.splitlines()
            
    for delims in comment_delim_sets:        
        log.debug("Trying delims: %r", delims)
        start_line = 0
        end_line = 0
        
        while start_line < MAX_SCAN_LINE:
            if delims[0] == '':
                comment = lines
            else:
                (start_line, end_line) = find_next_comment(end_line,
                                                           lines,
                                                           delims)
                if start_line == -1:
                    # No more comments; try next delim
                    break

                comment = lines[start_line:end_line]
                comment = strip_comment_chars(comment, delims)
            
            # We have a comment - is it a license block?
            tags = detector.id_license(comment)

            if tags is not None:
                for tag in tags:
                    # It is.
                    # Store away the info about the license for this file
                    (copyrights, license) = \
                             detector.extract_copyrights_and_license(comment, tag)
                    
                    # Store license info
                    copyrights = canonicalize_copyrights(copyrights)

                    copyrights_dict = {}
                    for c in copyrights:
                        copyrights_dict[c] = 1

                    licenses.append({
                        'tag': tag,
                        'copyrights': copyrights_dict,
                        'text': license
                    })                

            if delims[0] == '':
                # We did the whole file in one go; try next delim
                break

        if licenses:
            # Once we found at least one license, we assume all licenses use
            # the same delim, so we stop
            break

    if not licenses:
        # We also note if a comment is "suspicious" - in other words,
        # if we don't detect a license but there is a suspicious
        # comment, it suggests we should check the file by hand to 
        # see if our script needs improving.
        #
        # There are a lot of files which are Copyright AOSP and nothing
        # else. Perhaps I should file a bug... The distinction made 
        # here is to eliminate false positives for suspicion.
        tag = "none"
        
        if re.search("[Cc]opyright", content):
            tag = "suspiciousCopyright"
            
            if re.search("Copyright[\d\s,\(chC\)-]+The Android Open Source Pr",
                         content):
                tag = "suspiciousAndroid"
            # Things more likely to have an actual license text
            if re.search("[Ll]icen[cs]e|[Pp]ermi(t|ssion)|[Rr]edistribut",
                         content):
                tag = "suspiciousLicensey"
        
        licenses.append({
            'tag': tag,
        })                
                
    return licenses


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


# Returns the first line which is part of the next comment in the block, and
# the first line which is not (which can therefore be fed straight back in as
# the new starting_from value). Returns start_line of -1 if no comment found.
def find_next_comment(starting_from, lines, delims):
    end_line   = starting_from
    start_line = -1
    
    start_re = re.compile("^\s*%s" % re.escape(delims[0]))
    invert_end = False
    
    if len(delims) == 3:
        end_re = re.compile(re.escape(delims[2]))             
    elif len(delims) == 1:
        # This regexp actually looks for lines which _are_ in the comment,
        # because negative lookahead assertions are 2x slower. Hence the need
        # for result inversion.
        end_re = re.compile("^\s*(%s|$)" % re.escape(delims[0]))
        invert_end = True

    # Find start
    for i in range(starting_from, len(lines)):
        match = start_re.search(lines[i])
        if match:
            start_line = i
            log.debug("Found start line: %i", i)
            break

    # No more comments
    if start_line == -1:
        log.debug("No start line found - EOF")
        return -1, None

    # Find end
    found_end = False
    # Begin on the same line to account for single-line /* */
    for i in range(start_line, len(lines)):
        match = end_re.search(lines[i])
        end_line = i
        
        if invert_end:
            match = not match
        
        if match:
            log.debug("Found end line: %i", end_line)
            found_end = True
            break

    if start_line == end_line and len(delims) == 3:
        # Single-line comment of /* */ type. There could be a set of them
        # Fast forward and see
        while len(lines) > end_line + 1 and \
              start_re.search(lines[end_line + 1]) and \
              end_re.search(lines[end_line + 1]):
            end_line = end_line + 1

    if len(delims) == 3 or \
       (len(delims) == 1 and not found_end):
        # In these two cases, we are actually on the last comment line, so...
        log.debug("Adding 1 to end_line")
        end_line += 1

    assert start_line != end_line
    
    return start_line, end_line


def canonicalize_copyrights(copyrights):
    # Clean up individual lines
    for i in range(len(copyrights)):
        copyrights[i] = ws.collapse(copyrights[i])
        # Remove end cruft
        copyrights[i] = re.sub("[\*#\s/]+$", "", copyrights[i])
    
    return copyrights


def strip_comment_chars(comment, delims):
    prefix = delims[0]
    if len(delims) == 3:
        cont   = delims[1]
        suffix = delims[2]
    elif len(delims) == 1:
        cont   = delims[0]
        suffix = None
    else:
        raise Error("Invalid delimiter length in delims: %s" % delims)
        
    # Strip prefix
    prefix_re = re.compile("^\s*%s\s?" % re.escape(prefix))
    comment[0] = re.sub(prefix_re, "", comment[0])

    # Strip suffix
    if suffix:
        suffix_re = re.compile("\s*%s" % re.escape(suffix))
        comment[-1] = re.sub(suffix_re, "", comment[-1])

    # Allow multiple occurrences of cont char or last cont char
    cont_re = re.compile("^\s*%s+\s?" % re.escape(cont))
    for i in range(1, len(comment)):
        # Strip continuation char
        comment[i] = re.sub(cont_re, "", comment[i])
        # Strip trailing whitespace and cruft
        # (Also */ terminators from comments where each line is a single
        # "multi-line" comment)
        comment[i] = re.sub("[\*\/#\s]*$", "", comment[i])

    return comment

