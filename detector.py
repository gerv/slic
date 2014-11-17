# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# A module to detect licenses in blocks of text, and split them into their
# component parts.
#
# The key API is "get_license_info", which takes a filename and returns
# information about its license(s). Pass "details=True" in the params to get
# details on the copyright lines and the license text itself.
###############################################################################
import re
import ws
import logging
import copy

import ws
import config

logging.basicConfig(filename="slic.log")
log = logging.getLogger("slic")

DEFAULT_MAX_LINES_IN_LICENSE = 50
# This number is fairly performance-sensitive
MAX_SCAN_BYTES = 32768
MAX_GAP_LINES = 200

class Detector(object):    
    def __init__(self, license_data, params={}):
        """Set up the class's internal data"""
        self._group_names_to_tags = {}
        self._flat_license_data = {}
        
        self._license_data = copy.deepcopy(license_data)
        self._preprocess(self._license_data, None)

        self._details = params.get('details', False)
        
        # Things to ignore on a line - not a copyright line, and not the
        # license
        self._cruft_re = re.compile("""Derived\ from
                                       |Target\ configuration
                                       |[Cc]ontributed\ by
                                       |File:
                                       |File\ speex
                                       |Authors?:
                                       |[Vv]ersion
                                       |Written\ by
                                       |Linux\ for
                                       |You\ can\ look
                                       |available\ under
                                       """, re.VERBOSE)

    def _preprocess(self, license_data, parent):
        """This function, called recursively, prepares the data structure the
        detector will use. It does some sanity-checking, then caches compiled
        versions of all the necessary regexps at the right point in the
        structure.
        """
        matches = []
        
        for (tag, info) in license_data.iteritems():            
            if not tag:
                raise Exception("Missing tag in license data")

            if re.match("_", tag):
                raise Exception("Hit tag %s starting with underscore" % tag)

            # Bad things happen if we use the same name twice; detect this
            # condition and bail so it can be fixed.
            if tag in self._flat_license_data:
                raise Exception("Duplicate tag %s in license data" % tag)
            else:
                self._flat_license_data[tag] = info

            if parent is not None:
                info['_parent'] = parent
                
            # Python regexp group names have to be identifiers, but we want
            # the freedom to use more characters than this in tags. So we
            # make a compatible group name, and have a hash to map back.
            groupname = re.sub("[^a-zA-Z0-9_]", "_", tag)
            self._group_names_to_tags[groupname] = tag
            
            matches.append("(?P<" + groupname + ">" + info['match'] + ")")

            # Compile or find the appropriate bits of data for determining
            # the extent of the license block
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

            if 'cancel' in info:
                info['cancel'] = set(info['cancel'])

        # Python "only supports 100 named capturing groups", although it seems
        # to actually count groups of any sort, which means it's non-trivial
        # to work out when you have to actually split! So we leave headroom.
        # Our structure certainly has more than this many entries at the top
        # level, we create a set of regexps and apply them sequentially.
        grouplimit = 80

        license_data['_match_res'] = []
        
        while len(matches) > grouplimit:
            section = matches[:grouplimit]
            matches = matches[grouplimit:]
            license_data['_match_res'].append(re.compile("|".join(section)))

        license_data['_match_res'].append(re.compile("|".join(matches)))

        for (tag, info) in license_data.iteritems():            
            # Recurse if necessary
            if 'subs' in info:
                self._preprocess(info['subs'], info)

    def _fill_in_from_parent(self, info, key):
        """If a member is not present, find the nearest present value from
        the parents, or default to the 'match' member at the top level.
        """
        retval = None
        pointer = info
        
        while pointer and retval is None:
            if key in pointer:
                retval = pointer[key]
            else:
                if '_parent' in pointer:
                    pointer = pointer['_parent']
                else:
                    # Top level
                    retval = re.compile(info['match'])

        if retval is None:
            log.warning("_fill_in_from_parent found None; info: %r" % info)
            
        info[key] = retval

    def get_license_info(self, filename):    
        """Find the license or licenses in a file. Returns a list of license 
        objects. The only guaranteed value in a license object is the 'tag', 
        which may be 'none'.
        """
        fin = open(filename, 'r')
        try:
            content = fin.read(MAX_SCAN_BYTES)
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
            return []

        lines = content.splitlines()
                
        for delims in comment_delim_sets:        
            log.debug("Trying delims: %r", delims)
            start_line = 0
            end_line = 0
            most_recent_end_line = 0
            
            # We break out if any of the following are true:
            #
            # * The delim is "" and we have executed the loop once
            # * We have run out of comments in the file
            # * We have found at least one license and the most recent one was
            #   more than MAX_GAP_LINES ago
            while 1:
                if most_recent_end_line - start_line > MAX_GAP_LINES:
                    log.debug("Ending: > MAX_GAP_LINES without license")
                    break
                    
                if delims[0] == '':
                    comment = lines
                else:
                    (start_line, end_line) = self._find_next_comment(end_line,
                                                                     lines,
                                                                     delims)
                    if start_line == -1:
                        # No more comments; try next delim
                        log.debug("Ending: no more comments")
                        break

                    comment = lines[start_line:end_line]
                    comment = self._strip_comment_chars(comment, delims)
                
                # We have a comment - is it a license block?
                tags = self._find_license(comment)

                if tags is not None:
                    # It is.
                    most_recent_end_line = end_line
                    
                    for tag in tags:
                        license = {
                            'tag': tag
                        }
                        
                        if self._details:
                            # Store away the info about the license for this
                            # file
                            (copyrights, text) = \
                                               self._find_details(comment, tag)
                            copyrights = self._clean_copyrights(copyrights)

                            # De-dupe identical copyright lines
                            copyrights_dict = {}
                            for c in copyrights:
                                copyrights_dict[c] = 1

                            license['copyrights'] = copyrights_dict
                            license['text'] = text
                        
                        licenses.append(license)                

                if delims[0] == '':
                    # We did the whole file in one go; try next delim
                    log.debug("Ending: blank delimiter so just one pass")
                    break

            if licenses:
                # Once we found at least one license, we assume all licenses
                # use the same delim, so we don't try any further delims.
                break

        if not licenses:
            # We also note if a comment is "suspicious" - in other words,
            # if we don't detect a license but there is a suspicious
            # comment, it suggests we should check the file by hand to 
            # see if our script needs improving.
            #
            # There are a lot of files which are Copyright AOSP and nothing
            # else. The distinction made here is so we can eliminate false
            # positives for suspicion.
            tag = "none"
            text = None
            
            if re.search("[Cc]opyright", content):
                tag = "suspiciousCopyright"
                
                if re.search("Copyright[\d\s,\(chC\)-]+The Android Open Sourc",
                             content):
                    tag = "suspiciousAndroid"
                # Things more likely to have an actual license text
                else:
                    match = re.search("[Ll]icen[cs]e|[Pp]ermi(t|ssion)|[Rr]edistribu",
                                      content)
                    if match:
                        tag = "suspiciousLicensey"
                        # text = match.group(0)

            license = { 'tag': tag }
            if text is not None:
                license['text'] = text
                
            licenses.append(license)
                    
        return licenses

    def _find_next_comment(self, starting_from, lines, delims):
        """Returns the first line which is part of the next comment in the 
        block, and the first line which is not (which can therefore be fed 
        straight back in as the new starting_from value). Returns start_line of
        -1 if no further comment found.
        """
        end_line   = starting_from
        start_line = -1
        
        start_re = re.compile("^\s*%s" % re.escape(delims[0]))
        invert_end = False
        
        if len(delims) == 3:
            end_re = re.compile(re.escape(delims[2]))             
        elif len(delims) == 1:
            # This regexp actually looks for lines which _are_ in the comment,
            # because negative lookahead assertions are 2x slower. Hence the
            # need for result inversion.
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
                log.debug("Including next line from set of /* */ comments")
                end_line = end_line + 1
            
            log.debug("Adjusted end line: %i", end_line)

        if len(delims) == 3 or \
           (len(delims) == 1 and not found_end):
            # In these two cases, we are actually on the last comment line
            # so...
            log.debug("Adding 1 to end_line")
            end_line += 1

        assert start_line != end_line
        
        return start_line, end_line

    def _clean_copyrights(self, copyrights):
        """Clean up individual copyright lines"""
        for i in range(len(copyrights)):
            copyrights[i] = ws.collapse(copyrights[i])
            # Remove end cruft
            copyrights[i] = re.sub("[\*#\s/]+$", "", copyrights[i])
        
        return copyrights

    def _strip_comment_chars(self, comment, delims):
        """Remove all the starting (and ending, if appropriate) comment chars
        from a block comment, to leave just the text.
        """
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

            # If this is a multi-line comment but the suffix appears on the 
            # first line, it's of the form where every line is its own 
            # mini-comment. (This happens most often with /* */.) If so, change
            # the "cont" to the "start" to have it stripped off all lines.
            if re.search(suffix_re, comment[0]) and len(comment) > 1:
                log.debug("Multi-line comment with prefix/suffix on each line")
                cont = prefix

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

    def _find_license(self, comment):
        """Find all matching licenses in a particular comment. Entry function
        for the recursively-called function below. Returns a sorted list.
        """
        retval = None
        
        linear_comment = " ".join(comment)
        linear_comment = ws.collapse(linear_comment)

        # log.debug("Looking in text: %s\n\n" % linear_comment)
        tags = self._find_license_against(self._license_data, linear_comment)

        if len(tags):
            # Remove all tags that other tags cancel
            for tag in tags.copy():
                data = self._flat_license_data[tag]
                if 'cancel' in data:
                    tags.difference_update(data['cancel'])

            retval = list(tags)
            retval.sort()
            log.info("Found license(s): %s" % "/".join(retval))
        else:
            log.debug("No license found in comment")
            
        return retval


    def _find_license_against(self, license_data, comment):
        """Recursive function to precisely identify all matching licenses in
        a particular comment. Recurses to get more specific. Returns a set.
        """
        tags = set()
        retval = None

        # For each regexp (remember, they are split up due to limits in
        # Python)...
        for match_re in license_data['_match_res']:
            # For each match found...
            for match in match_re.finditer(comment):
                # For each actual hit in the match object...
                hits = match.groupdict()            
                for hit in match.groupdict():
                    if hits[hit] is not None:
                        # Make a note of it in a de-duping hash
                        log.debug("Hit: %s" % hit)
                        tags.add(self._group_names_to_tags[hit])

        for tag in tags.copy():
            log.debug("Found license %s" % tag)
            if 'subs' in license_data[tag]:
                log.debug("Checking for sub-types")
                newtags = self._find_license_against(license_data[tag]['subs'],
                                                     comment)
                if len(newtags):
                    log.debug("Replacing license %s with %r" % (tag, newtags))
                    tags.discard(tag)
                    tags.update(newtags)
                else:
                    log.debug("Sticking with base flavour")
            
        return tags

    def _find_details(self, text, tag):
        """Given a comment (array of lines) and a license tag, find the
        license text block corresponding to that license in the comment.
        Also extract any copyright lines. The incoming comment text should
        have already been stripped of comment markers.

        Heuristics galore.
        """
        license = []
        copyrights = []
        in_copyrights = False
        
        info = self._flat_license_data[tag]
        
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
                # there are multiple licenses in a file :-| No good option.
                break

            log.debug("Line: %s" % line)
            # This check is in two parts because the first check is a lot
            # cheaper than the second
            if re.search("[Cc]opyright", line):
                # The second half of the conditional attempts to catch the
                # (erroneous) form where the person puts their name before
                # the date or copyright symbol
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
                    log.debug("Another (C) line starting with year or symbol")
                    copyrights.append("Copyright " + line)
                elif self._cruft_re.search(line): 
                    log.debug("Line with ignorable cruft")
                    in_copyrights = False
                else:
                    # Continuation line of previous copyright line
                    log.debug("CopyConti line: %s" % line)
                    copyrights[-1] = copyrights[-1] + " " + line

        if start_line == -1:
            log.warning("Can't find start line for license '%s'!" % tag)
            return [], []
            
        # Find license end, starting from text end
        end_line = -1
        for i in range(len(text) - 1, -1, -1):
            line = text[i]
            
            if info['_end_re'].search(line):
                log.debug("Last license line: %s" % line)
                end_line = i
                    
                if (end_line - start_line < info['maxlines']):
                    # If the license seems too long, keep looking in case
                    # there's a nearer end line, otherwise break. This deals
                    # with files where there's multiple copies of the license
                    # text, e.g. concatenated files
                    break
        else:
            if end_line == -1:
                log.warning("Can't find end line for license '%s'!" % tag)
                end_line = len(text)

        log.debug("License extent: line %i to %i" % (start_line, end_line))
        license = text[start_line:end_line + 1]

        license    = self._remove_initial_rubbish(license)
        copyrights = self._remove_initial_rubbish(copyrights)
        
        return copyrights, license

    def _remove_initial_rubbish(self, comment):
        """While comment chars have been removed, some license blocks still
        have repeated cruft at the start of the line (often a different
        type of comment char. Or they have leading whitespace.
        
        We can't just remove all leading whitespace line-by-line as that can
        mess up formatting. However, we can remove any common prefix of
        whitespace or random rubbish. For the moment, take whatever's on
        the first line off every line.
        """
        if not comment:
            return comment
        
        match = re.search("^([\s\*#\-/]+)", comment[0])
        if match:
            rubbish = match.group(0)
            # Last char is made optional; it can be pre-text whitespace which
            # doesn't appear on blank lines
            rubbish_re = re.compile("^" + re.escape(rubbish) + "?")

            for i in range(len(comment)):
                comment[i] = re.sub(rubbish_re, "", comment[i])

        return comment
