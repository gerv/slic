#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################

import sys
import re
import json
import argparse
from os.path import dirname, exists, join, basename, split
from jinja2 import Environment, PackageLoader
import ws
import textwrap
import cgi

import logging
logging.basicConfig(filename="clic.log", level=logging.DEBUG)
log = logging.getLogger("clic")

# A couple of functions used in the template
#
# Pop all keys from a dict which match a regexp or list of regexps, and return
# the dict of the popped items
def pop_by_re(regexps, dic):
    result = {}
    
    if type(regexps) == str:
        regexps = [regexps]

    for regexp in regexps:
        key_re = re.compile(regexp)
        for k in dic.keys():
          if key_re.search(k):
            result[k] = dic.pop(k)

    return result


def template_exists(template):
     path = join(dirname(sys.argv[0]), "templates", template)
     return exists(path)


# A mapping to reduce the number of times you get a given copyright holder
# listed "twice" because their name has multiple forms
canonical_holders = {
    'Silicon Graphics': 'Silicon Graphics Computer Systems, Inc.',
    'The Regents of the University of California. All rights reserved.':
               'Regents of the University of California. All rights reserved.',
    'Mozilla Foundation.': 'Mozilla Foundation',
    'Android Open Source Project': 'The Android Open Source Project',
    'The Android Open Source Project All rights reserved.': 'The Android Open Source Project. All rights reserved.',
    'Student Information Processing Board of the Massachusetts Institute of Technology.':
        'by the Student Information Processing Board of the Massachusetts Institute of Technology',
    'World Wide Web Consortium, (Massachusetts Institute of Technology, Institut National de Recherche en Informatique et en Automatique, Keio University). All':
        'World Wide Web Consortium, (Massachusetts Institute of Technology, Institut National de Recherche en Informatique et en Automatique, Keio University). All Rights Reserved.',
    'Renesas Technology.': 'Renesas Technology',
}

def tidy_holder(holder):
    # Ick. Prevent "obvious" duplications of copyright holders
    if holder in canonical_holders:
        holder = canonical_holders[holder]
        
    return holder


# Take an array of integer years and turn it into a comma-separated string
# list of years and ranges
def _join_years(years):
    if not years:
        return ""
    
    # uniq
    set = {}
    map(set.__setitem__, years, [])
    years = set.keys()

    # sort
    years.sort()

    years_as_str = []
    range_start = None
    for i in range(len(years) - 1):
        if years[i + 1] == years[i] + 1:
            if not range_start:
                range_start = years[i]
        elif range_start:
            # No range continuation, pending value; finish range
            years_as_str.append("%i-%i" % (range_start, years[i]))
            range_start = None
        else:
            # No range continuation, no pending value
            years_as_str.append(str(years[i]))

    # Final year
    if range_start:
        # Pending value; finish range
        years_as_str.append("%i-%i" % (range_start, years[-1]))
    else:
        # No pending value
        years_as_str.append(str(years[-1]))

    return ", ".join(years_as_str)
            

# Take a string list of years and ranges and turn it into an array of integer
# years
def _split_years(string):
    if not string:
        return []
    
    years = []
    for piece in string.split(','):
        if re.search("^\s*$", piece):
            # Blank line
            continue

        cw_piece = ws.collapse(piece)
        
        if re.search("-", piece):
            # Range
            rng = piece.split('-')

            if not rng[0] or not rng[1]:
                continue
                
            if (re.search("^\s*$", rng[0])):
                continue

            if (re.search("^\s*$", rng[1])):
                years.append(_canonicalize_year(rng[0]))
                continue
            
            start = _canonicalize_year(rng[0])
            end = _canonicalize_year(rng[1])

            if start < 1970 or end > 2030:
                continue
                
            for i in range(start, end + 1):
                years.append(i)
        elif len(cw_piece) > 5:
            # Space-separated years? 5 rather than 4 to try and deal with
            # foolish typos such as "20010".
            sp_years = [_canonicalize_year(year) for year in piece.split()]
            years.extend(sp_years)
        elif len(cw_piece) == 4:
            # Single year
            years.append(_canonicalize_year(piece))
        else:
            log.warning("Year with strange length: '%s'" % cw_piece) 

    return years


# Make string year an integer, and expand from 2 digits to 4 if necessary
def _canonicalize_year(year):
    assert year != ''
    year = int(year)
    
    if year > 100 and year < 1970:
        log.warning("Strange year: '%s'" % year) 
    
    if year < 100:
        if year > 70:
            year = 1900 + year
        else:
            year = 2000 + year

    return year


###############################################################################
# main()
###############################################################################
def main():
    env = Environment(loader=PackageLoader('__main__', 'templates'),
                      trim_blocks=True,
                      extensions=['jinja2.ext.do'])

    parser = argparse.ArgumentParser(description=\
                                    'Collate and process license information.')
    parser.add_argument('--template', metavar="<template>",
                       help='Render the given template name')

    args = parser.parse_args()

    # Load occurrence data file
    occurrences = json.load(open("occurrences.json"))

    # Rejig data structure so top-level key is the tag instead of the license
    # text hash, and value is a list of the corresponding license objects
    bytag = {}

    for hash, occurrence in occurrences.items():
        tag = occurrence['tag']
        if tag in bytag:
            bytag[tag].append(occurrence)
        else:
            bytag[tag] = [occurrence]

    # For some licenses, we have a specific set text and so even if small
    # variants are found, we choose to ignore them and amalgamate all the
    # files and copyright holders into a single entry
    single_entry_licenses = ['BSD4Clause_RTFM', 'BSDProtection', 'FreeType_fulltext',
                             'libjpeg', 'GPL20_BSD', 'MIROS', 'BSD3Clause_urlref',
                             'W3C_urlref']
    
    for tag in bytag:
        if not tag in single_entry_licenses:
            continue

        log.info("Creating single entry for tag %s" % tag)
        license = {
            'tag': tag,
            'copyrights': [],
            'files': [],
            'text': None,
        }

        for data in bytag[tag]:
            license['copyrights'].extend(data['copyrights'])
            license['files'].extend(data['files'])
            license['text'] = data['text']

        bytag[tag] = [license]

    # Insert 2x<br> at para breaks for formatting on small screens
    for tag in bytag:
        for data in bytag[tag]:
            if not 'text' in data:
                continue

            html = "\n".join(data['text'])
            html = cgi.escape(html)
            
            # Empty line before bullets
            html = re.sub(r"\n\s*([0-9]\.|\*|-)", r"\n\n \1", html)

            # Empty line above acknowledgement text
            html = re.sub(r"(acknowledge?ment:\n)", r"\1\n", html)
 
            # While we're at it...
            html = re.sub("``", '&#8220;', html)
            html = re.sub("''", '&#8221;', html)

            # Replace all empty lines by double <br>s
            html = re.sub(r"(\n){2,}", '<br><br>', html)
            
            data['html'] = html

    # Post-process and amalgamate copyright lines
    # \xa9 is the copyright symbol
    copy_re = re.compile("""Copyright\s*
                            (\(C\)|\xa9)?\s*
                            (?P<years>[-\d,\s]*)\s
                            (?P<holder>.*)$""",
                         re.IGNORECASE | re.VERBOSE)

    for tag in bytag:
        for data in bytag[tag]:
            if not 'copyrights' in data:
                continue
            
            copyrights = data['copyrights']

            # Amalgamate years
            holders = {}
            for i in range(len(copyrights)):
                match = copy_re.search(copyrights[i])
                if match:
                    hits = match.groupdict()
                    log.info("Hits: %r" % hits)
                    holder = tidy_holder(hits['holder'])
                    years = _split_years(hits['years'])
                    if holder in holders:
                        holders[holder].extend(years)
                    else:
                        holders[holder] = years
                else:
                    log.warning("(C) line doesn't match re: %s" % copyrights[i])

            # Rebuild copyright lines
            clean_copyrights = []
            for holder in holders:
                log.debug("Years: %r" % holders[holder])
                years = _join_years(holders[holder])
                spacer = " " if years else ""
                copyright = u"Copyright \xa9 %s%s%s" % (years,
                                                        spacer,
                                                        holder)
                log.debug("Clean C line: %s" % copyright)
                clean_copyrights.append(copyright)

            data['copyrights'] = clean_copyrights

    # Reconcile Bison exception, which can be in a different comment to the GPL
    # license and so is noted as a different "license" :-|
    def resolve_bison_exception(bisonfile):
        log.debug("Trying to resolve bisonexception for %s" % bisonfile)
        for tag in bytag:
            if not re.search("^GPL30", tag):
                continue
            
            for data in bytag[tag]:
                gplfiles = data['files']
                for gplfile in gplfiles:
                    if gplfile == bisonfile:
                        log.info("Resolved bisonexception for %s" % bisonfile)
                        gplfiles.remove(gplfile)

                        # Make sure GPL goes away if there are no GPLed files
                        # left
                        if not gplfiles:
                            bytag[tag].remove(data)

                        if not bytag[tag]:
                            del(bytag[tag])
                            
                        return True

        log.warning("Unable to resolve bisonexception for %s" % bisonfile)
        return False

    if 'Bisonexception' in bytag:
        for data in bytag['Bisonexception']:
            bisonfiles = data['files']
            for bisonfile in bisonfiles:
                resolve_bison_exception(bisonfile)
        del bytag['Bisonexception']

    # Sometimes a file header says "see file FOO for the license". If so, we tag
    # it with a tag including 'fileref'. We must now go through all files so
    # tagged and make sure that a corresponding license file has been found and
    # included.

    # Make a hash lookup table of all files found which match any of the special
    # filenames. It's always possible that the Android people will have renamed
    # the file to "NOTICE"...
    fileref_names = {
        'copying_fileref':    ['COPYING', 'NOTICE'],
        'copyright_fileref':  ['COPYRIGHT', 'NOTICE'],
        'license_fileref':    ['LICENSE', 'NOTICE'],
        'bzip2_fileref':      ['LICENSE', 'NOTICE'],
        'BSD_fileref_xiph':   ['COPYING', 'NOTICE'],
        'BSD_fileref':        ['LICENSE', 'NOTICE', 'README'],
        'BSD_fileref2':       ['LICENSE.txt'], # sic
        'BSD_fileref3':       ['README'],
        'MIT_fileref':        ['COPYING', 'NOTICE'],
        'MIT_GPL20_fileref':  ['MIT-LICENSE.txt', 'NOTICE'],
        'FreeType_fileref':   ['LICENSE.txt', 'docs/FTL.TXT', 'NOTICE'],
        'ISC_fileref':        ['LICENSE', 'NOTICE'],
        'libjpeg_fileref':    ['README'],        
        'jsimdext_fileref':   ['jsimdext.inc'],
        # Po files have some "same license as" boilerplate
        'po_fileref':         ['COPYING', 'LICENSE', 'NOTICE']
    }

    # Unique
    unique_filenames = {}
    for fileref in fileref_names:
        map(unique_filenames.__setitem__, fileref_names[fileref], [])

    license_files = {}
    license_files_re = re.compile("^(" + "|".join(unique_filenames.keys()) + ")")

    # Gather list of "LICENSE"-type files        
    for tag in bytag:
        for data in bytag[tag]:
            files = data['files']
            for file in files:
                filename = basename(file)
                if license_files_re.match(filename):
                    license_files[file] = data['tag']

    # For each file marked as having a "fileref" license, see if an appropriate
    # file in a higher directory is present and has been included somewhere.
    # Assuming it has, we can ignore the fileref file itself because the
    # license has been noted when we included the referred-to file.
    def find_license_file_for(file, license_file_names):
        log.debug("File path: %s" % file)
        for license_file_name in license_file_names:
            log.debug("Trying to find license file: %s" % license_file_name)
            dir = dirname(file)
            log.debug("Starting directory: %s" % dir)
            while dir != "." and dir != "./gecko":
                log.debug("Looking for %s" % join(dir, license_file_name))
                if join(dir, license_file_name) in license_files:
                    log.debug("Found license %s in dir: %s" % (license_file_name, dir))
                    return True
                # Up one level
                dir = re.sub("/$", "", dir)
                dir = dirname(dir)
                log.debug("Moving up to dir: %s" % dir)
            
        log.debug("Found no license file for %s" % file)
        return False

    fileref_problem_files = []
    fileref_problem_dirs = {}

    for tag in bytag:
        if not re.search("fileref", tag):
            continue

        if not tag in fileref_names:
            log.warning("No license file info for fileref tag '%s'" % tag)
            continue

        license_file_names = fileref_names[tag]
        
        for data in bytag[tag]:
            log.debug("Checking filerefs for tag %s" % tag)
            for file in data['files']:
                # We ignore some copies of header files which are also found
                # elsewhere
                log.info(file)
                if re.search("xulrunner-sdk", file):
                    continue
                    
                if not find_license_file_for(file, license_file_names):
                    fileref_problem_files.append(file)
                    fileref_problem_dirs[split(file)[0]] = 1

    # Render output
    if args.template:
        template = env.get_template(args.template)
        log.info("Rendering")
        print template.render({
            'licenses': bytag,
            'pop_by_re': pop_by_re,
            'template_exists': template_exists,
            'fileref_problem_files': fileref_problem_files,
            'fileref_problem_dirs': fileref_problem_dirs,
            'license_files': license_files
        }).encode('utf-8')


if __name__ == "__main__":
    main()
