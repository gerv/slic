#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################

class Results(dict):
    def load_json(self, data):
        # Populates the Results from a JSON file
        self.__init__(json.load(data))

    def pop_by_re(self, regexps):
        # Returns another Results and modifies this one
        result = Results()
        
        if type(regexps) == str:
            regexps = [regexps]

        for regexp in regexps:
            key_re = re.compile(regexp)
            for k in dic.keys():
              if key_re.search(k):
                result[k] = dic.pop(k)

        return result

    def unify(self):
        # Changes all the contained tags to have one-item lists
        for tag, data in self.iteritems():        
            license = {
                'tag': tag,
                'copyrights': [],
                'files': [],
                'text': None,
            }

            for data in datalist:
                license['copyrights'].extend(data['copyrights'])
                license['files'].extend(data['files'])
                license['text'] = data['text']

            self[tag] = [license]

    def iterdata(regexp):
        tag_re = re.compile(regexp)
        # Returns all members of all lists
        # Takes optional regexp to match tags against
        return itertools.chain(data for tag, data in self.itersomething()
                                                         if tag_re.search(tag))
 
