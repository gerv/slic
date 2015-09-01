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
            with open(initval, 'r') as jsonfile:
                data = json.load(jsonfile)

        # Rejig data structure so top-level key is the tag instead of the
        # unification hash value, and value is a list of the corresponding
        # license objects
        bytag = {}

        for occurrence in data:
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
                'copyrights': [],
                'files': []
            }

            for data in datalist:
                if 'copyrights' in data:
                    license['copyrights'].extend(data['copyrights'])
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
 
