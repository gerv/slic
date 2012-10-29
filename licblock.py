import re
import hashlib
import os.path
from config import get_config, get_delims

import logging
# logging.basicConfig(filename="relic.log", level=logging.DEBUG)
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
    
    for delims in comment_delim_sets:
        # Hack to get around strange Python single member empty tuple behaviour
        if type(delims) == str:
            delims = [delims]
        
        log.debug("Trying delims: %r", delims)
        end_line = 0

        while 1:
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
            license_tag = identify_license(comment)
            if license_tag:
                log.debug("License found")
                # Extract copyright lines into array
                (copyrights, license) = extract_copyrights(comment)
                license = tidy_license(license, license_tag, filename)
                
                # Canonicalize them
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

            if delims[0] == '':
                break
                
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
        end_re = re.compile("^\s*(?!%s|\s)" % re.escape(delims[0]))

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


def extract_copyrights(comment):
    start_patterns = re.compile("""(
      (?P<mpl>The\ contents\ of\ this\ file\ are\ subject\ to\ the\ Mozilla)
    | (?P<mpl2>This\ Source\ Code\ Form\ is\ subject\ to\ the\ terms\ of)
    | (?P<gnu>This\ program\ is\ free\ software:\ you\ can\ redistribute\ it)
    | (?P<apache2>Licensed\ under\ the\ Apache\ License,?\ Version\ 2\.0)
    | (?P<hpnd>Permission\ to\ use,\ copy,\ modify,(?:\ and)?\ distribute)
    | (?P<mit>(?:Permission\ is\ hereby\ granted,
                 \ (?:free\ of\ charge
                      |without\ written\ agreement)
              |licensed\ under\ the\ MIT))
    
    | (?P<bsd>Redistribution\ and\ use\ of\ this\ software|
              Redistribution\ and\ use\ in\ source\ and\ binary\ forms)
    | (?P<bsdfileref>Licensed\ under\ the\ New\ BSD\ license|
                     The\ program\ is\ distributed\ under\ terms\ of\ BSD
                     \ license|
                     Use\ of\ this\ source\ code\ is\ governed\ by\ a
                     \ BSD\-style\ license)
    | (?P<gnupermissive>Copying\ and\ distribution\ of\ this\ file,\ with
                        \ or\ without)
    | (?P<icu>ICU\ License)
    | (?P<jpnic>license\ is\ obtained\ from\ Japan\ Network\ Information\ Center)
    | (?P<gemmell>This\ software\ is\ supplied\ to\ you\ by\ Matt\ Gemmell)
    | (?P<ofl10>SIL\ OPEN\ FONT\ LICENSE\ Version\ 1\.0)
    | (?P<ofl11>This\ Font\ Software\ is\ licensed\ under\ the\ SIL\ Open
                \ Font\ License,\ Version\ 1\.1)
    | (?P<iscgeneral>This\ program\ is\ made\ available\ under\ an\ ISC\-style
                     \ license)
    )""",
        re.VERBOSE | re.IGNORECASE)

    copyrights = []
    license = []
    in_copyrights = False
    had_blank = True
    
    for line in comment:
        # Ignorable lines, e.g. modelines
        if re.search("-\*-|vim\:", line):
            log.debug("Ignorable line: %s" % line)
            continue
            
        if re.search("^\s*(Copyright|COPYRIGHT) ", line):
            log.debug("Copyright line: %s" % line)
            copyrights.append(line)
            in_copyrights = True
            continue
            
        if in_copyrights:
            if re.search("^\s*$", line): 
                log.debug("Blank line (while in copyrights)")
                # Blank line
                in_copyrights = False
            elif start_patterns.search(line):
                # Normal license line
                log.debug("First license line: %s" % line)
                license.append(line)
                in_copyrights = False
            else:
                # Continuation line
                log.debug("CopyConti line: %s" % line)
                copyrights[-1] = copyrights[-1] + " " + line
                had_blank = False
        elif had_blank and re.search("^\s*$", line):
            # 2nd or subsequent blank line
            log.debug("Multiple blank line")
            continue
        else:
            # Normal license line
            log.debug("License line: %s" % line)
            license.append(line)
            had_blank = re.search("^\s*$", line)

    if had_blank:
        # Remove final blank line
        license = license[0:-1]
    
    return copyrights, license


def canonicalize_copyrights(copyrights):
    for i in range(len(copyrights)):
        copyrights[i] = collapse_whitespace(copyrights[i])
    
    return copyrights   


def tidy_license(license, license_tag, filename):
    # This is where we collect hacks to try and remove cruft which gets caught
    # up in various license blocks

    if not license:
        return license
        
    # Some files rather pointlessly include the name of the file in the license
    # block, which makes them all different :-| However, there also exist files
    # with names like "copyright", which makes life more complex. We exclude
    # all extensionless filenames from this, to be safe.
    (base, ext) = os.path.splitext(filename)
    if ext == '':
        filename = filename + ".xxxdontmatchanything"
    
    ignoreme = re.compile("""
    %s
    """ % re.escape(os.path.basename(filename)),
    re.VERBOSE | re.IGNORECASE)
    
    # Strip non-copyright lists of names or blank lines from end of licenses    
    if re.search("mit|hpnd|mpl", license_tag):
        while re.search("""Author
                         |Contributor
                         |@
                         |Initial\ Developer
                         |Original\ Code
                         |^\s*$
                         """,
                        license[-1],
                        re.IGNORECASE | re.VERBOSE):
            log.debug("Removing attrib line: %s" % license[-1])
            license = license[0:-1]

    # Loop downwards so we can remove items
    is_blank = False
    for i in range(len(license) - 1, -1, -1):

        # Remove general lines we don't like
        if ignoreme.search(license[i]):
            log.debug("Removing ignoreme line: %s" % license[i])
            license = license[:i] + license[i + 1:]
            continue
            
        # Remove multiple successive blank lines
        if re.search("^\s*$", license[i]):
            if is_blank:
                license = license[:i] + license[i + 1:]
            is_blank = True
        else:
            is_blank = False
    
    # Remove any trailing blank lines
    if license:
        while re.search("^\s*$", license[-1], re.IGNORECASE):
            license = license[0:-1]
            
    return license

    
def identify_license(license):
    line_license = canonicalize_comment(license)
    
    parts_pattern = re.compile("""(
      (?P<mpl>The\ contents\ of\ this\ file\ are\ subject\ to\ the\ Mozilla)
    | (?P<gpl>under\ the\ terms\ of\ the\ GNU\ (?:General\ )?Public\ License)
    | (?P<lgpl>under\ the\ terms\ of\ the\ GNU\ (?:Library|Lesser)\ General
               \ Public)
    | (?P<gpllgpltri>in\ which\ case\ the\ provisions\ of\ the\ GPL\ or\ the
                     \ LGPL\ are\ applicable)
    | (?P<mplgpltri>Mozilla\ Public\ License.*or\ the\ GNU\ General)
    | (?P<mpl2>This\ Source\ Code\ Form\ is\ subject\ to\ the\ terms\ of)
    | (?P<apache2>Licensed\ under\ the\ Apache\ License,?\ Version\ 2\.0)
    
    | (?P<ace>Use\ of\ this\ source\ code\ is\ governed\ by\ the\ ACE
              \ copyright\ license)
    | (?P<bsdheader>Redistribution\ and\ use\ of\ this\ software|
                    Redistribution\ and\ use\ in\ source\ and\ binary\ forms)
    | (?P<bsdsource>Redistributions\ of\ source\ code\ must\ retain\ the)
    | (?P<bsdbinary>Redistributions\ in\ binary\ form\ must\ reproduce\ the)
    | (?P<bsdendorse>Neither\ the\ names?\ of|
                     The\ name\ of\ the\ author\ may\ not\ be\ used)
    | (?P<bsdadvert>All\ advertising\ materials\ mentioning)
    | (?P<bsdlebedev>Modified\ versions\ must\ be\ clearly\ marked\ as\ such)
    
    | (?P<bsdgeneral1>Licensed\ under\ the\ New\ BSD\ license)
    | (?P<bsdgeneral2>The\ program\ is\ distributed\ under\ terms\ of\ BSD
                      \ license)
    | (?P<bsdgeneral3>Use\ of\ this\ source\ code\ is\ governed\ by\ a
                      \ BSD\-style\ license)

    | (?P<seecopying>See\ the\ file\ COPYING)
    
    | (?P<mit>(?:Permission\ is\ hereby\ granted,
                 \ (?:free\ of\ charge
                      |without\ written\ agreement)
              |licensed\ under\ the\ MIT))
    | (?P<hpnd>Permission\ to\ use,\ copy,\ modify,(?:\ and)?\ distribute)
    
    | (?P<pd>[Pp]ublic\ [Dd]omain)
    | (?P<gnupermissive>Copying\ and\ distribution\ of\ this\ file,\ with
                        \ or\ without)

    | (?P<gplexception>part\ or\ all\ of\ the\ Bison\ parser\ skeleton|
                       is\ built\ using\ GNU\ Libtool,\ you\ may\ include|
                       configuration\ script\ generated\ by\ Autoconf|
                       need\ not\ follow the\ terms\ of\ the\ GNU\ General|
                       As\ a\ special\ exception,\ when\ this\ file\ is\ read\ by\ TeX)
    
    | (?P<icu>ICU\ License)
    | (?P<jpnic>license\ is\ obtained\ from\ Japan\ Network\ Information\ Center)
    | (?P<gemmell>This\ software\ is\ supplied\ to\ you\ by\ Matt\ Gemmell)
    | (?P<ofl10>SIL\ OPEN\ FONT\ LICENSE\ Version\ 1\.0)
    | (?P<ofl11>This\ Font\ Software\ is\ licensed\ under\ the\ SIL\ Open
                \ Font\ License,\ Version\ 1\.1)
    | (?P<edl>the\ Eclipse\ Distribution)
    | (?P<iscgeneral>This\ program\ is\ made\ available\ under\ an\ ISC\-style
                     \ license)
    | (?P<costellodisclaimer>Regarding\ this\ entire\ document\ or\ any
                             \ portion\ of\ it)
    
    | (?P<vp8patent>and\ otherwise\ transfer\ this\ implementation\ of\ VP8)
    )""",
        re.VERBOSE | re.IGNORECASE)

    start = 0
    tags = []
    
    while 1:
        match = parts_pattern.search(line_license, start)
    
        if match:
            parts = match.groupdict()
            tags.extend([part for part in parts if parts[part]])
            start = match.end()
        else:
            break

    if tags:        
        log.debug("License found: %s" % "/".join(tags))
        return "/".join(tags)
    else:
        log.debug("No license found in comment")
        return False


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

        
