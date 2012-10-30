import re
import hashlib
import os.path
from config import get_config, get_delims
import detector

import logging
log = logging.getLogger("relic")

# "licenses" is an accumulating result parameter
def get_license_block(filename, licenses):
    fin = open(filename, 'r')
    try:
        content = fin.read()
    finally:
        fin.close()
    
    log.info("Processing: %s", filename)

    # Get comment delimiter info for this file.
    comment_delim_sets = get_delims(filename)
    
    if not comment_delim_sets:
        # We can't handle this type of file
        log.info("No comment delimiters found")
        return

    lines = content.splitlines()
    license_found = False
    default_tag = 'none'
    
    for delims in comment_delim_sets:
        # Hack to get around strange Python single member empty tuple behaviour
        # XXX find the proper fix; test with rpm.spec files
        if type(delims) == str:
            delims = [delims]
        
        log.debug("Trying delims: %r", delims)
        start_line = 0
        end_line = 0
        
        while start_line < 300:
            if delims[0] == '':
                comment = lines
            else:
                (start_line, end_line) = find_next_comment(end_line,
                                                           lines,
                                                           delims)

                if start_line == -1:
                    # No more comments
                    break

                comment = lines[start_line:end_line]
                comment = strip_comment_chars(comment, delims)
            
            # We have a comment - is it a license block?
            license_tag = detector.id_license(comment)
            if license_tag:
                license_found = True
                log.debug("License found: %s" % license_tag)
                
                (copyrights, license) = \
                  detector.extract_copyrights_and_license(comment, license_tag)
                
                copyrights = canonicalize_copyrights(copyrights)

                copyrights_by_md5 = {}
                for c in copyrights:
                    copyrights_by_md5[hashlib.md5(c).hexdigest()] = c

                # Store license info
                line_license = canonicalize_comment(license)
                lic_md5 = hashlib.md5(line_license).hexdigest()

                if lic_md5 in licenses:
                    licenses[lic_md5]['copyrights'].update(copyrights_by_md5)
                    licenses[lic_md5]['files'].append(filename)
                else:
                    licenses[lic_md5] = {
                        'text': license,
                        'tag': license_tag,
                        'copyrights': copyrights_by_md5,
                        'files': [filename]
                    }

            elif re.match("copyright", canonicalize_comment(comment), re.IGNORECASE):
                default_tag = "suspicious"
                
            if delims[0] == '':
                # We did the whole file in one go
                break
        
    if not license_found:
        if default_tag in licenses:
            licenses[default_tag]['files'].append(filename)
        else:
            licenses[default_tag] = {
                'text': '',
                'tag': default_tag,
                'files': [filename]
            }            
                
    return


# Returns the first line which is part of the next comment in the block, and
# the first line which is not (which can therefore be fed straight back in as
# the new starting_from value). Returns start_line of -1 if no comment found.
def find_next_comment(starting_from, lines, delims):
    end_line   = starting_from
    start_line = -1
    
    start_re = re.compile("^\s*%s" % re.escape(delims[0]))
    
    if len(delims) == 3:
        end_re = re.compile("\s*%s" % re.escape(delims[2]))             
    elif len(delims) == 1:
        # Negative lookahead assertion: whitespace not followed by the
        # delimiter (needed because delimiter can be multiple chars, e.g. //)
        # Requires one extra character to as to amalgamate blocks separated
        # only by blank lines (a common but irritating case).
        end_re = re.compile("^\s*(?!%s|\s).+$" % re.escape(delims[0]))

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
        log.debug("Finding end: checking line %s" % lines[i])
        match = end_re.search(lines[i])
        end_line = i
        if match:
            log.debug("Found end line: %i", end_line)
            found_end = True
            break

    if len(delims) == 3 or \
       (len(delims) == 1 and not found_end):
        # In these two cases, we are actually on the last comment line, so...
        log.debug("Adding 1 to end_line")
        end_line += 1

    assert start_line != end_line
    
    return start_line, end_line


def canonicalize_copyrights(copyrights):
    for i in range(len(copyrights)):
        copyrights[i] = collapse_whitespace(copyrights[i])
    
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
        raise Error("Unknown delimiter length in delims: %s" % delims)
        
    # Strip prefix
    prefix_re = re.compile("\s*%s\s?" % re.escape(prefix))
    comment[0] = re.sub(prefix_re, "", comment[0])

    # Strip suffix
    if suffix:
        suffix_re = re.compile("\s*%s" % re.escape(suffix))
        comment[-1] = re.sub(suffix_re, "", comment[-1])
    
    cont_re = re.compile("^\s*%s+\s?" % re.escape(cont))
    for i in range(1, len(comment)):
        # Strip continuation char
        comment[i] = re.sub(cont_re, "", comment[i])
        # Strip trailing whitespace
        comment[i] = re.sub("\s*$", "", comment[i])

    return comment


def canonicalize_comment(comment):
    line = " ".join(comment)

    line = collapse_whitespace(line)
    line = line.lower()
    
    return line


def collapse_whitespace(line):
    # Collapse whitespace
    line = re.sub("\s+", " ", line)

    # Strip leading and trailing whitespace
    line = re.sub("^\s", "", line)
    line = re.sub("\s$", "", line)
    
    return line
