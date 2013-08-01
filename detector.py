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
logging.basicConfig(filename="relic.log", level=logging.DEBUG)
log = logging.getLogger("relic")

DEFAULT_MAX_LINES_IN_LICENSE = 50

# For each license, 'match' is a regexp which identifies that license or
# license family uniquely, when matched against a large runon string of the
# entire comment. 'subs' is a set of sub-flavours of that license. Once a type
# is detected, matches are run against the 'match' member of all the subs. If
# none are detected, you have the base flavour; otherwise you have the
# sub-flavour. This can happen recursively (see 'BSD2Clause').
#
# Once a block has been identified as containing a particular license, you
# search from the start for a line matching 'start', and from the end
# for a line matching 'end', and take all the text in between.
#
# License tags (the dict keys) must be unique throughout the structure.
_license_parts = {
    # MPL
    'MPL11': {
        'start':  r"The contents of this file are subject to the",
        'match':  r"subject to the Mozilla Public License Version 1.1",
        'end':    r"Contributor|All Rights Reserved|Initial Developer",
        'subs': {
            'MPL11_GPL20_LGPL21': { # Mozilla
                'start':  r"The contents of this (file|package) are subject to the",
                'match':  r"Alternatively, the .*either the GNU General",
                'end':    r"terms of any one of the MPL, the GPL or the LGPL"
            },            
        }
    },
    'MPL20': {
        'start':  r"Source Code Form [Ii]s subject to the terms of the Mozilla",
        'match':  r"Mozilla Public License, v\. 2\.0",
        'end':    r"You can obtain one at http://mozilla\.org/MPL/2\.0/",
        'subs': {
            'MPL20fulltext': {
                'start':  r"Mozilla Public License Version 2.0",
                'match':  r"each individual or legal entity",
                'end':    r"by the Mozilla Public License, v\. 2\.0"
            },            
            'MPL20incompatible': {
                'start':  r"Source Code Form [Ii]s subject to the terms of the Mozilla",
                'match':  r"Incompatible With Secondary Licenses",
                'end':    r"by the Mozilla Public License, v\. 2\.0"
            },            
        }
    },
    # GPL
    'GPL20urlref': {
        'start':  r"Licensed under the GPL \(http://www\.gnu\.org/licenses/gpl.html\) license",
        'match':  r"Licensed under the GPL \(http://www\.gnu\.org/licenses/gpl.html\) license",
        'end':    r"Licensed under the GPL \(http://www\.gnu\.org/licenses/gpl.html\) license"
    },    
    'GPL30': {
        'start':  r"is free software[:;] you can redistribute it|This file is part of the",
        'match':  r"GNU General Public License.*version 3[ ,]",
        'end':    r"along with this program|gnu\.org/licenses/|0211[01].*USA",
        'subs': {
            'GPL20or30': {
                'start':  r"is free software[:;] you can redistribute it|This file is part of the",
                'match':  r"version 2",
                'end':    r"along with this program|gnu\.org/licenses/|0211[01].*USA"
            },
            'GPL30withautoconfexception1': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"the output of Autoconf when processing",
                'end':    r"modified version as well"
            },
        }
    },
    'GPL20': {
        'start':  r"is free software; you can redistribute it|This software is licensed under the terms of the GNU",
        'match':  r"GNU General Public License.*version 2[ ,.]" + \
                  r"|version 2 .*GNU General Public License" + \
                  r"|Licensed under the GPL-2 or later",
        'end':    r"021(10|11|39).*USA|for more details|any later version|Free Software Foundation",
        'subs': {
            'GPL20withautoconfexception1': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"configuration script generated by Autoconf",
                'end':    r"rest of that program"
            },
            'GPL20withlibtoolexception': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"GNU Libtool",
                'end':    r"021(10|11|39).*USA|for more details|any later version"
            },
            'GPL20withtexinfoexception': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"when this file is read by TeX",
                'end':    r"Texinfo was invented"
            },
            'GPL20BSD': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"Alternatively.*BSD license",
                'end':    r"See README and COPYING for more details"
            },
        }
    },
    # XXX Also catches 2.0 at the moment
    'LGPL21': {
        'start':  r"is free software; you can redistribute it",
        'match':  r"GNU (Lesser|Library) General Public License.*version 2",
        'end':    r"021(10|11|39).*USA|lgpl\.html|Free Software Foundation|of the License",
        'subs': {
            'LGPL21_MPL11_GPL20': {
                'start':  r"is free software; you can redistribute it",
                'match':  r"Alternatively, the.*Mozilla Public License",
                'end':    r"\(at your option\) any later version"
            },
            'LGPL21_MPL11': { # Cairo
                'start':  r"is free software; you can redistribute it",
                'match':  r"should have received a copy of the MPL along with",
                'end':    r"governing rights and limitations"
            }
        }
    },
    'GPL20fileref': {
        'start':  r"This program can be distributed under the terms of the GNU GPL",
        'match':  r"This program can be distributed under the terms of the GNU GPL",
        'end':    r"See the file COPYING"
    },
    'Bisonexception': {
        'start':  r"As a special exception, you may",
        'match':  r"of the Bison parser skeleton",
        'end':    r"of Bison"
    },
    'GPL20withautoconfexception2': {
        'start':  r"This (program|file) is free software",
        'match':  r"configuration script generated by Autoconf",
        'end':    r"rest of that program"
    },
    # Apache
    'Apache20': {
        'start':  r"Licensed under the Apache License,? Version 2\.0" + \
                  r"|Licensed to the Apache Software Foundation \(ASF\)",
        'match':  r"under the Apache License,? Version 2\.0",
        'end':    r"the License\.?|licenses/LICENSE-2\.0",
        'maxlines': 12
    },
    'Apache20fulltext': {
        'start':  r"Apache License",
        'match':  r"\"Legal Entity\" shall mean the union of the acting",
        'end':    r"warranty or additional liability",
        'maxlines': 12
    },
    'Apache20fileref': {
        'start':  r"Use of this source code is governed by the Apache License, Version 2\.0",
        'match':  r"Use of this source code is governed by the Apache License, Version 2\.0",
        'end':    r"See the COPYING file for details"
    },
    # Permissive
    'HPND': {
        'start':  r"[Pp]ermission to use, copy, modify,?(?: and(/or)?)? distribute",
        'match':  r"[Pp]ermission to use, copy, modify,?(?: and(/or)?)? distribute",
        'end':    r"(OF|FOR) THIS SOFTWARE|express or implied warranty" + \
                  r"|written prior permission|supporting documentation" + \
                  r"|MODIFICATIONS|prior written authorization",
        'subs': {
            'genericpermissive4': {
                'start':  r"Permission to use, copy, modify,?(?: and(/or)?)? distribute",
                'match':  r"freely granted",
                'end':    r"is preserved",
            },
        }
    },
    'MIT': {
        'start':  r"Permission is hereby granted, " + \
                  r"(?:free of charge|without written agreement)" + \
                  r"|licensed under the MIT",
        'match':  r"Permission is hereby granted, " + \
                  r"(?:free of charge|without written agreement)" + \
                  r"|licensed under the MIT",
        'end':    r"SOFTWARE\.|copyright holder|OR MODIFICATIONS|MATERIALS",
        'subs': {
            'mit_gpl20_fileref': { # jQuery
                'start': r"Dual licensed under the MIT",
                'match': r"Dual licensed under the MIT.*and GPL",
                'end':   r"jquery\.com/License|licenses\."
            },
            'mit_bsd_hybrid': {
                'start': r"Permission is hereby granted, free of charge",
                'match': r"Redistributions? in binary form",
                'end':   r"SOFTWARE"
            },
            'mitboost': {
                'start': r"Boost Software License",
                'match': r"Boost Software License",
                'end':   r"SOFTWARE"
            }
         }
    },
    'mitfileref': {
        'start':  r"This is free software.*distribute,? or modify",
        'match':  r"terms of the MIT/X [lL]icense",
        'end':    r"terms of the MIT/X [lL]icense|with this distribution",
    },
    'miturlrefcubiq': {
        'start':  r"Released under MIT license, http://cubiq\.org/license",
        'match':  r"Released under MIT license, http://cubiq\.org/license",
        'end':    r"Released under MIT license, http://cubiq\.org/license",
    },
    'boosturlref': {
        'start':  r"Distributed under the Boost Software License, Version 1\.0",
        'match':  r"Distributed under the Boost Software License, Version 1\.0",
        'end':    r"http://www\.boost\.org/LICENSE_1_0\.txt",
    },
    'BSD2Clause': {
        'start':  r"Redistribution and use of this software" + \
                  r"|Redistribution and use in source and binary forms",
        'match':  r"Redistribution and use of this software" + \
                  r"|Redistribution and use in source and binary forms",
        'end':    r"SUCH DAMAGE",
        'subs': {
            'BSD3Clause': {
                'start':  r"Redistribution and use of this software" + \
                          r"|Redistribution and use in source and binary",
                'match':  r"name.*(may|must) not be used to" + \
                          r"|Neither the (author|name).*may be used to" + \
                          r"|The name of the company nor the name of the author",
                'end':    r"SUCH DAMAGE",
                'subs': {
                    'BSD4Clause': {
                        'start':  r"Redistribution and use of this software" + \
                                  r"|Redistribution and use in source and",
                        'match':  r"advertising materials",
                        'end':    r"SUCH DAMAGE",
                        'subs': {
                            # For all of these, the 4th clause is not a problem
                            # because it has been waived, either permanently
                            # or for our use of the code.
                            'BSD4ClauseUC': {
                                'start':  r"Redistribution and use of this software" + \
                                          r"|Redistribution and use in source and",
                                'match':  r"University of California",
                                'end':    r"SUCH DAMAGE|PURPOSE"
                            },
                            'BSD4ClauseNetBSD': {
                                'start':  r"Redistribution and use of this software" + \
                                          r"|Redistribution and use in source and",
                                'match':  r"The NetBSD Foundation",
                                'end':    r"SUCH DAMAGE|PURPOSE"
                            },
                            'BSD4ClauseRTFM': {
                                'start':  r"Redistribution and use of this software" + \
                                          r"|Redistribution and use in source and",
                                'match':  r"RTFM, Inc",
                                'end':    r"SUCH DAMAGE|PURPOSE"
                            },
                            # This one, there is no waiver but we aren't using
                            # the code, even though the Android people have
                            # copied the notice into a NOTICE file we read.
                            # So we detect it separately so we can ignore it.
                            'BSD4ClauseWinning': {
                                'start':  r"Redistribution and use of this software" + \
                                          r"|Redistribution and use in source and",
                                'match':  r"Winning Strategies, Inc",
                                'end':    r"SUCH DAMAGE|PURPOSE"
                            },
                        }
                    }
                }
            },
            'BSD4ClauseCompact': {
                'start':  r"Redistribution and use in source and binary",
                'match':  r"in all such forms.*advertising materials",
                'end':    r"A PARTICULAR PURPOSE",
                'subs': {
                    'BSD4ClauseCompactUC': {
                        'start':  r"Redistribution and use in source and binary",
                        'match':  r"University of California, Berkeley",
                        'end':    r"A PARTICULAR PURPOSE",
                    },
                }
            },
            'BSD4ClauseSSLeay': {
                'start':  r"Redistribution and use in source and binary",
                'match':  r"Eric Young|Tim Hudson",
                'end':    r"SUCH DAMAGE",
            }
        }
    },
    'bsdprotection': {
        'start': r"BSD PROTECTION LICENSE",
        'match': r"BSD PROTECTION LICENSE",
        'end':   r"OF SUCH DAMAGES"
    },
    'bsdfileref': {
        'start':  r"Use of this source code is governed by a BSD-style",
        'match':  r"Use of this source code is governed by a BSD-style",
        'end':    r"LICENSE|source tree"
    },
    'bsdfileref2': {
        'start':  r"BSD, see LICENSE for details",
        'match':  r"BSD, see LICENSE for details",
        'end':    r"BSD, see LICENSE for details"
    },
    'bsd2urlref': {
        'start': r"The program is distributed under terms of BSD",
        'match': r"The program is distributed under terms of BSD",
        'end':   r"licenses/bsd-license\.php"
    },
    'bsd3urlref': {
        'start': r"Licensed under the New BSD license",
        'match': r"Licensed under the New BSD license",
        'end':   r"licenses/BSD-3-Clause"
    },
    'bsdfilerefxiph': {
        'start': r"USE, DISTRIBUTION AND REPRODUCTION",
        'match': r"BSD-STYLE SOURCE LICENSE INCLUDED WITH",
        'end':   r"TERMS BEFORE DISTRIBUTING"
    },
    'bsdurlrefyui': {
        'start': r"Code licensed under the BSD License",
        'match': r"http://developer\.yahoo\.com/yui/license\.html",
        'end':   r"http://developer\.yahoo\.com/yui/license\.html"
    },
    'bsdurlrefpaj': {
        'start': r"Distributed under the BSD License",
        'match': r"See http://pajhome\.org\.uk/crypt/md5 for details",
        'end':   r"http://pajhome\.org\.uk/crypt/md5 for details"
    },
    'copyingfileref': {
        'start':  r"See the file COPYING for copying permission",
        'match':  r"See the file COPYING for copying permission",
        'end':    r"See the file COPYING for copying permission"
    },
    'copyrightfileref': {
        'start':  r"See the accompanying file \"COPYRIGHT\" for",
        'match':  r"See the accompanying file \"COPYRIGHT\" for",
        'end':    r"NO WARRANTY FOR THIS SOFTWARE"
    },
    'webmurlref': {
        'start':  r"This code is licensed under the same terms as WebM",
        'match':  r"This code is licensed under the same terms as WebM",
        'end':    r"Additional IP Rights Grant|Software License Agreement"
    },
    'gnupermissive1': {
        'start':  r"Copying and distribution of this file, with or without",
        'match':  r"Copying and distribution of this file, with or without",
        'end':    r"notice are preserved"
    },
    'gnupermissive2': {
        'start':  r"This (Makefile\.in|file) is free software",
        'match':  r"This (Makefile\.in|file) is free software.*with or without modifications",
        'end':    r"PARTICULAR PURPOSE|notice is preserved" 
    },
    'genericpermissive1': {
        'start':  r"This software is provided \"as is\"; redistribution and",
        'match':  r"This software is provided \"as is\"; redistribution and",
        'end':    r"possibility of such damage" 
    },
    'genericpermissive2': {
        'start':  r"This material is provided \"as is\", with absolutely no",
        'match':  r"This material is provided \"as is\", with absolutely no",
        'end':    r"above copyright notice" 
    },
    'genericpermissive3': {
        'start':  r"You may redistribute unmodified or modified versions",
        'match':  r"I shall in no event be liable",
        'end':    r"using this software" 
    },
    'genericpermissive4': {
        'start':  r"You may use this program",
        'match':  r"as desired without restriction",
        'end':    r"as desired without restriction" 
    },
    'genericpermissive5': {
        'start':  r"You may use, copy, modify and distribute this code",
        'match':  r"use\) and without fee",
        'end':    r"this code" 
    },
    'icu': {
        'start':  r"ICU License - ICU",
        'match':  r"ICU License - ICU",
        'end':    r"respective owners"
    },
    'jpnic': {
        'start':  r"The following License Terms and Conditions apply",
        'match':  r"The name of JPNIC may not be used",
        'end':    r"POSSIBILITY OF SUCH DAMAGES"
    },
    'OFL10': {
        'start':  r"This Font Software is licensed",
        'match':  r"SIL Open Font License, Version 1\.0",
        'end':    r"IN THE FONT SOFTWARE"
    },
    'OFL11': {
        'start':  r"This Font Software is licensed",
        'match':  r"SIL Open Font License, Version 1\.1",
        'end':    r"IN THE FONT SOFTWARE"
    },
    'ISCfileref': {
        'start':  r"This program is made available under an ISC-style license",
        'match':  r"This program is made available under an ISC-style license",
        'end':    r"file LICENSE for details"
    },
    'sgib': {
        'start': r"SGI Free Software B License",
        'match': r"SGI Free Software B License",
        'end':   r"oss\.sgi\.com/projects/FreeB/"
    },
    'nvidia': {
        'start': r"NVIDIA Corporation\(\"NVIDIA\"\) supplies this software to you",
        'match': r"NVIDIA Corporation\(\"NVIDIA\"\) supplies this software to you",
        'end':   r"OF SUCH DAMAGE"
    },
    'freetypefileref': {
        'start': r"This file is part of the FreeType project",
        'match': r"This file is part of the FreeType project",
        'end':   r"fully"
    },
    'freetypefulltext': {
        'start': r"The FreeType Project LICENSE",
        'match': r"The FreeType Project LICENSE",
        'end':   r"http://www\.freetype\.org"
    },
    'W3Curlref': {
        'start': r"(program|work) is distributed under the W3C('s|\(r\)) Software" + \
                 r"|The following software licensing rules apply",
        'match': r"(program|work) is distributed under the W3C('s|\(r\)) Software" + \
                 r"|The following software licensing rules apply",
        'end':   r"A PARTICULAR PURPOSE|for more details|copyright-software"
    },
    'whatwg': {
        'start': r"You are granted a license to use",
        'match': r"use, reproduce and create derivative works of",
        'end':   r"this document"
    },
    'zlibref': {
        'start': r"Licensed under the zlib/libpng license",
        'match': r"Licensed under the zlib/libpng license",
        'end':   r"Licensed under the zlib/libpng license"
    },
    'zlibfileref': {
        'start': r"For conditions of distribution and use, see copyright notice",
        'match': r"distribution and use, see copyright notice in zlib.h",
        'end':   r"notice in zlib.h"
    },
    'bzip2fileref': {
        'start': r"This program is released under the terms",
        'match': r"This program is released under the terms of the license contained in the file LICENSE.",
        'end':   r"the file LICENSE"
    },
    'jsimdextfileref': {
        'start': r"For conditions of distribution and use, see copyright notice in jsimdext\.inc",
        'match': r"For conditions of distribution and use, see copyright notice in jsimdext\.inc",
        'end':   r"For conditions of distribution and use, see copyright notice in jsimdext\.inc"
    },
    'Python20': {
        'start': r"This module is free software, and you",
        'match': r"same terms as Python itself",
        'end':   r"OR MODIFICATIONS"
    },
    'CDDL10': {
        'start': r"The contents of this file are subject",
        'match': r"Common Development and Distribution License",
        'end':   r"under the License"
    },
    'Libpng': {
        'start': r"The PNG Reference Library is supplied",
        'match': r"The PNG Reference Library is supplied",
        'end':   r"appreciated"
    },
    'libpngfileref': {
        'start': r"This code is released under the libpng license",
        'match': r"This code is released under the libpng license",
        'end':   r"license in png.h"
    },
    'curlurlref': {
        'start': r"This software is licensed as described",
        'match': r"http://curl\.haxx\.se/docs/copyright\.html",
        'end':   r"either express or implied"
    },
    'libjpegfileref': {
        'start': r"part of the Independent JPEG Group's software",
        'match': r"part of the Independent JPEG Group's software",
        'end':   r"accompanying README file"
    },
    'libjpeg': {
        'start': r"The authors make NO WARRANTY or representation",
        'match': r"for the use of any IJG author's name",
        'end':   r"by the product vendor"
    },
    'zlib': {
        'start': r"This software is provided 'as-is'",
        'match': r"use this software for any purpose, including commercial applications",
        'end':   r"any source distribution"
    },
    'EPL10': {
        'start': r"Licensed under the Eclipse Public License, Version 1\.0",
        'match': r"Licensed under the Eclipse Public License, Version 1\.0",
        'end':   r"under the License"
    },  
    'EPL10fulltext': {
        'start': r"Eclipse Public License - v 1\.0",
        'match': r"The Eclipse Foundation is the initial Agreement Steward",
        'end':   r"any resulting litigation"
    },
    'EDLEPLurlref': {
        'start': r"This program and the accompanying materials",
        'match': r"http://www\.eclipse\.org/org/documents/edl-v10\.html",
        'end':   r"http://www\.eclipse\.org/org/documents/edl-v10\.html"
    },
    'CPL10': {
        'start': r"THE ACCOMPANYING PROGRAM|DEFINITIONS",
        'match': r"COMMON PUBLIC LICENSE",
        'end':   r"any resulting litigation"
    },  
    'miros': {
        'start': r"Provided that these terms and disclaimer and all",
        'match': r"immediate fault when using",
        'end':   r"using the work as intended"
    },  
    'naist': {
        'start': r"Use, reproduction, and distribution of this software",
        'match': r"in no event shall NAIST be liable",
        'end':   r"program is concerned"
    },  
    'mozillalookelsewhere': {
        'start': r"Please see the file toolkit/content/license\.html",
        'match': r"Please see the file toolkit/content/license\.html",
        'end':   r"name or logo|licensing\.html"
    },
    'gliblookelsewhere': {
        # glib license is LGPL
        'start': r"This file is distributed under the same license as the glib package",
        'match': r"This file is distributed under the same license as the glib package",
        'end':   r"This file is distributed under the same license as the glib package"
    },
    # PD
    'pd': {
        'start': r"[Pp]ublic [Dd]omain|PUBLIC DOMAIN",
        'match': r"[Pp]ublic [Dd]omain|PUBLIC DOMAIN",
        'end':   r"[Pp]ublic [Dd]omain|PUBLIC DOMAIN|conceived",
        'subs': {
            'CC0': {
                'start': r"Any copyright is dedicated to the Public Domain",
                'match': r"http://creativecommons\.org/(publicdomain/zero/1\.0/|licenses/publicdomain/)",
                'end':   r"http://creativecommons\.org/(publicdomain/zero/1\.0/|licenses/publicdomain/)"
            }
        }
    },
    'nocopyrightableinfo': {
        'start': r"This header was automatically generated from",
        'match': r"no copyrightable information",
        'end':   r"no copyrightable information"
    },
    'sqliteblessing': {
        'start': r"The author disclaims copyright",
        'match': r"In place of a legal notice, here is a blessing",
        'end':   r"taking more than you give"
    },
    'unicodeurlref': {
        'start': r"For terms of use, see http://www\.unicode\.org/terms_of_use\.html",
        'match': r"For terms of use, see http://www\.unicode\.org/terms_of_use\.html",
        'end':   r"For terms of use, see http://www\.unicode\.org/terms_of_use\.html"
    }
}

starts = {}
ends = {}
maxlines = {}

def _preprocess(struct):
    matches = []
    for (name, info) in struct.items():
        if not name:
            continue

        matches.append("(?P<" + name + ">" + info['match'] + ")")
        starts[name] = re.compile(info['start'])
        ends[name]   = re.compile(info['end'])
        maxlines[name] = info.get('maxlines', DEFAULT_MAX_LINES_IN_LICENSE)
        if 'subs' in info:
            _preprocess(info['subs'])
    
    struct['_match_re'] = re.compile("|".join(matches))


_preprocess(_license_parts)


def id_license(comment):
    linear_comment = " ".join(comment)
    linear_comment = ws.collapse(linear_comment)

    tag = _id_license_against(_license_parts, linear_comment)

    if tag:
        log.debug("Found license: %s" % tag)
        return tag
    else:
        log.debug("No license found in comment")
        return None


def _id_license_against(parts, comment):
    match = parts['_match_re'].search(comment)
    
    if match:
        hits = match.groupdict()
        tags = [hit for hit in hits if hits[hit]]
        if len(tags) > 1:
            log.warning("Found multiple licenses: %s" % "/".join(tags))
        tag = tags[0]
        log.debug("License match: %s" % tag)
        if 'subs' in parts[tag]:
            log.debug("Checking for sub-types")
            newtag = _id_license_against(parts[tag]['subs'], comment)
            if newtag:
                log.debug("Overriding license %s with %s" % (tag, newtag))
                tag = newtag
            else:
                log.debug("Sticking with base flavour")
        
        return tag

    return None


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

def extract_copyrights_and_license(text, tag):
    license = []
    copyrights = []
    in_copyrights = False

    start_line = -1
    end_line = -1    
    
    # Find copyrights and start
    for i in range(len(text)):
        line = text[i]
        
        if start_line == -1 and starts[tag].search(line):
            log.debug("First license line: %s" % line)
            start_line = i
            in_copyrights = False
            # If we break here, we only find copyrights written above the
            # license. If we don't, we end up combining copyrights when
            # there are multiple licenses in a file :-|
            break
        
        if re.search("copyright ?[\d\(©]", line, re.IGNORECASE):
            log.debug("Copyright line: %s" % line)
            copyrights.append(line)
            in_copyrights = True
            continue
        
        if in_copyrights:
            if re.search("^\s*$", line): 
                log.debug("Blank line (while in copyrights)")
                # Blank line
                in_copyrights = False
            elif re.search("^\s*(\d{4}|©|\(C\))", line, re.IGNORECASE): 
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
        
        if ends[tag].search(line):
            log.debug("Last license line: %s" % line)
            end_line = i
                
            if (end_line - start_line < maxlines[tag]):
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

    license    = _remove_initial_rubbish(license)
    copyrights = _remove_initial_rubbish(copyrights)
    
    return copyrights, license


def _remove_initial_rubbish(comment):
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
            comment[i] = re.sub("^" + re.escape(rubbish) + "?", "", comment[i])

    return comment
