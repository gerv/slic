# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# A module to detect licenses in blocks of text, and split them into their
# component parts.
###############################################################################
import re
import ws
import logging
import copy

logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

DEFAULT_MAX_LINES_IN_LICENSE = 50

class Detector(object):    
    def __init__(self, license_data):
        self._group_names_to_tags = {}
        self._license_data = copy.deepcopy(license_data)
        self._preprocess(self._license_data, None)

    # This does some sanity-checking, then caches compiled versions of all the
    # regexps, either in the license data structure or the hashes just above.
    def _preprocess(self, license_data, parent):
        matches = []
        for (tag, info) in license_data.iteritems():            
            if not tag:
                raise Exception("Missing tag in license data struct")

            if re.match("_", tag):
                from pprint import pformat
                dta = pformat(license_data)
                prnt = pformat(parent)
                raise Exception("Hit tag %s starting with underscore; data: %s; parent: %s" % (tag, dta, prnt))

            info['_parent'] = parent
                
            # Python group names have to be identifiers, but we want the freedom
            # to use more characters than this in tags. So we make a compatible
            # group name, and have a hash to map back.
            groupname = re.sub("[^a-zA-Z0-9_]", "_", tag)
            
            # Bad things happen if we use the same name twice; detect this
            # condition and bail so it can be fixed.
            if groupname in self._group_names_to_tags:
                print "%r" % self._group_names_to_tags
                raise Exception("Duplicate groupname %s (from tag %s)" % (groupname, tag))
            else:
                self._group_names_to_tags[groupname] = tag

            matches.append("(?P<" + groupname + ">" + info['match'] + ")")
        
            if 'start' in info:
                info['_start_re'] = re.compile(info['start'])
            else:
                self._fill_in_from_parent(info, '_start_re')
                
            if 'end' in info:
                info['_end_re'] = re.compile(info['end'])
            else:
                self._fill_in_from_parent(info, '_end_re')
                
            if 'maxlines' not in info:
                info['maxlines'] = DEFAULT_MAX_LINES_IN_LICENSE
                
            if 'subs' in info:
                print("Preprocessing subs of %s" % tag) 
                self._preprocess(info['subs'], info)
                print("Returning from preprocessing tag %s" % tag)

        # Python "only supports 100 named capturing groups", although it seems
        # to have problems at 94...
        grouplimit = 90

        print "Setting _match_res on tag %s" % tag
        license_data['_match_res'] = []
        while len(matches) > grouplimit:
            section = matches[:grouplimit]
            matches = matches[grouplimit:]
            license_data['_match_res'].append(re.compile("|".join(section)))

        license_data['_match_res'].append(re.compile("|".join(matches)))

    def _fill_in_from_parent(self, info, key):
        """If a member is not present, find the nearest present value from
           the parents"""
        pointer = info
        while pointer and key not in pointer:
            pointer = pointer['_parent']

        if pointer:
            info[key] = pointer[key]
        else:
            info[key] = None

    def id_license(self, comment):
        retval = None
        
        linear_comment = " ".join(comment)
        linear_comment = ws.collapse(linear_comment)

        tags = self._id_license_against(self._license_data, linear_comment)

        if len(tags):
            retval = [tag for tag in tags.keys() if not tag.startswith("Ignore_")]
            retval.sort()
            log.warning("Found license(s): %s" % "/".join(retval))
        else:
            log.debug("No license found in comment")
            
        return retval


    def _id_license_against(self, parts, comment):
        tags = {}
        retval = None

        for match_re in parts['_match_res']:
            match = match_re.search(comment)
            
            if match:
                hits = match.groupdict()
                for hit in hits:
                    if hits[hit]:
                        tags[self._group_names_to_tags[hit]] = 1

        for tag in tags.keys():
            log.debug("Found license %s" % tag)
            if 'subs' in parts[tag]:
                log.debug("Checking for sub-types")
                newtags = self._id_license_against(parts[tag]['subs'], comment)
                if len(newtags):
                    log.debug("Overriding license %s with %r" % (tag, newtags))
                    del tags[tag]
                    tags.update(newtags)
                else:
                    log.debug("Sticking with base flavour")
            
        return tags


    # Things to ignore on a line - not a copyright line, and not the license
    cruft_re = re.compile("""Derived\ from
                             |Target\ configuration
                             |[Cc]ontributed\ by
                             |File:
                             |File\ speex
                             |Author:
                             |[Vv]ersion
                             |Written\ by
                             |Linux\ for
                             |You\ can\ look
                             """, re.VERBOSE)

    def extract_copyrights_and_license(self, text, tag):
        license = []
        copyrights = []
        in_copyrights = False
        
        info = self._license_data[tag]
        
        start_line = -1
        end_line = -1    
        
        # Find copyrights and start
        for i in range(len(text)):
            line = text[i]
            
            if start_line == -1 and info['_start_re'].search(line):
                log.debug("First license line: %s" % line)
                start_line = i
                in_copyrights = False
                # If we break here, we only find copyrights written above the
                # license. If we don't, we end up combining copyrights when
                # there are multiple licenses in a file :-|
                break

            log.debug("Line: %s" % line)
            if re.search("[Cc]opyright", line):
                if re.search("[Cc]opyright ?[\d\(©]", line) or \
                   re.search("[Cc]opyright.{0,50}?\d{4}", line):
                    log.debug("Copyright line: %s" % line)
                    copyrights.append(line)
                    in_copyrights = True
                    continue
            
            if in_copyrights:
                if re.search("^\s*$", line): 
                    log.debug("Blank line (while in copyrights)")
                    # Blank line
                    in_copyrights = False
                elif re.search("^\s*(\d{4}|©|\([Cc]\))", line): 
                    log.debug("Another copyright line starting with year or symbol")
                    copyrights.append("Copyright " + line)
                elif cruft_re.search(line): 
                    log.debug("Line with ignorable cruft")
                    in_copyrights = False
                else:
                    # Continuation line
                    log.debug("CopyConti line: %s" % line)
                    copyrights[-1] = copyrights[-1] + " " + line

        if start_line == -1:
            log.warning("Can't find start line for requested license '%s'!" % tag)
            return [], []
            
        # Find license end, starting from text end
        end_line = -1
        for i in range(len(text) - 1, -1, -1):
            line = text[i]
            
            if info['_end_re'].search(line):
                log.debug("Last license line: %s" % line)
                end_line = i
                    
                if (end_line - start_line < info['maxlines']):
                    # If the license seems too long, keep looking in case there's
                    # a nearer end line, otherwise break. This deals with files
                    # where there's multiple copies of the license text, e.g.
                    # concatenated files
                    break
        else:
            if end_line == -1:
                log.warning("Can't find end line for requested license '%s'!" % tag)
                end_line = len(text)

        log.debug("License extends from line %i to %i" % (start_line, end_line))
        license = text[start_line:end_line + 1]

        license    = self._remove_initial_rubbish(license)
        copyrights = self._remove_initial_rubbish(copyrights)
        
        return copyrights, license


    def _remove_initial_rubbish(self, comment):
        # Can't just remove all leading whitespace line-by-line as that can mess 
        # up formatting. However, we can remove any common prefix of whitespace or
        # random rubbish. For the moment, take off whatever's on the first line.
        if not comment:
            return comment
        
        match = re.search("^([\s\*#\-/]+)", comment[0])
        if match:
            rubbish = match.group(0)
            for i in range(len(comment)):
                # Last char is made optional; it can be pre-text whitespace which
                # doesn't appear on blank lines
                comment[i] = re.sub("^" + re.escape(rubbish) + "?",
                                    "",
                                    comment[i])

        return comment
