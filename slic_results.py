#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################
#
# The internal data structure here is a dict. The keys are Slic tag names,
# which identify a license. The values are a list of one or more occurrences
# of a bit of text which identifies that license. Each unique textual
# representation becomes a different item in the list. Attached to the text is
# a list of files where that text appeared, and a list of recognisable
# copyright lines parsed from the comment in which the text appears.
#
# So something like this:
#
# {
#   'GPL-2.0': [
#     {
#       'tag': 'GPL-2.0',
#       'files: ['/foo/bar.c', 'foo/quux.c'],
#     },
#     ...
#   ],
#   'BSD-2-Clause': [
#     {
#       'tag': 'BSD-2-Clause',
#       'files: ['/bedrock/fred.html', 'bedrock/wilma.html'],
#       'text': "Redistribution and use in source and binary forms ...",
#       'copyright': ["Copyright (C) 2000-1994 BC, Barney Rubble", ...]
#     },
#     {
#       'tag': 'BSD-2-Clause',
#       'files: ['/beatles/john.js', '/beatles/paul.js'],
#       'text': "Redistribution and use in source and/or binary forms..."
#     },
#     ...
#   ],
#   ...
# }
#

import json
import re
import itertools
import hashlib
from utils import collapse


# Function to remove false positive differences from a string or array of
# strings and then return a unique identifier for it
def make_hash(thing):
    if type(thing) == str:
        thing = [thing]

    line = " ".join(thing)
    line = re.sub("[\*\.,\-\d]+", "", line)
    line = utils.collapse(line)

    line = line.encode('ascii', errors='ignore')
    line = line.lower()
    hash = hashlib.md5(line).hexdigest()

    return hash


class SlicResults(dict):
    def load_json(self, initval):
        """Populates the Results from JSON, either as string or as filename.
           This function can be called more than once, and will merge in any
           new JSON files. (This is useful if you ran slic in parallel over
           different parts of the codebase.)
        """
        if re.match(r"^\s*\[", initval):
            data = json.loads(initval)
        else:
            data = json.load(open(initval))

        # Rejig data structure so it's a hash where the top-level key is the
        # tag and the value is a list of the corresponding license objects
        bytag = {}

        for occurrence in data:
            occurrence['copyrights'] = set(occurrence['copyrights'])
            tag = occurrence['tag']
            if tag in bytag:
                bytag[tag].append(occurrence)
            else:
                bytag[tag] = [occurrence]

        self.update(bytag)
        
    def pop_by_re(self, regexps):
        """Creates another SlicResults with all entries which match any of the
        regexps given, and removes them from this one.
        """
        subset = SlicResults()
        
        if type(regexps) == str:
            regexps = [regexps]

        for regexp in regexps:
            key_re = re.compile(regexp)
            for k in self.keys():
              if key_re.search(k):
                subset[k] = self.pop(k)

        return subset

    def unify(self):
        """Combines all of the items in the lists into a single item per tag.
        It does this by combining the lists of copyright holders and the lists
        of files, and taking the text from an (undefined) member of the set.
        """
        for tag, datalist in self.iteritems():        
            license = {
                'tag': tag,
                'copyrights': set(),
                'files': []
            }

            for data in datalist:
                if 'copyrights' in data:
                    license['copyrights'].update(data['copyrights'])
                if 'files' in data:
                    license['files'].extend(data['files'])
                if 'text' in data:
                    license['text'] = data['text']

            self[tag] = [license]

    def itervalues(self, regexp=""):
        """Returns an iterator which iterates over all items in the value lists
        """
        tag_re = re.compile(regexp)
        # Returns all members of all lists
        # Takes optional regexp to match tags against
        return itertools.chain.from_iterable(data for tag, data
                                                  in self.iteritems()
                                                  if tag_re.search(tag))
 
    def add_info(self, filename, license):
        # We store results with a unique key based on both tag and (if present)
        # license text hash; this keeps each different text separate.
        lic_key = license['tag']
        if 'text' in license and len(license['text']) > 0:
            lic_key = license['tag'] + "__" + make_hash(license['text'])

        if lic_key in self:
            # log.debug("Adding file %s to list" % filename)
            self[lic_key][0]['files'].append(filename)
            if 'copyrights' in license:
                self[lic_key][0]['copyrights'].update(license['copyrights'])
        else:
            # log.debug("Starting new file list with file %s" % filename)
            license['files'] = [filename]
            if 'copyrights' in license:
                license['copyrights'] = set(license['copyrights'])
            self[lic_key] = [license]

    def index_by_tag(self):
        """This does directly what writing the data out as JSON and loading it
           again does indirectly - removes the deduplicating hash keys in
           favour of plain tags.
        """
        tags_to_delete = []
        for external_tag, licenses in self.iteritems():
            internal_tag = licenses[0]['tag']  
            if internal_tag != external_tag:
                # This tag is one with a hash in it; reparent all the licenses
                self[internal_tag].extend(licenses)
                
                # Null this one out for later deletion
                tags_to_delete.append(external_tag)

        for tag in tags_to_delete:
            del self[tag]
    
    def to_list_string(self):
        return json.dumps(self.values(), indent=2)
