# -*- coding: utf-8 -*-
###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###############################################################################

###############################################################################
# Data format
#
# Blocks are identified by tags, which are equal to or begin with SPDX license
# identifiers (where they exist). If it's multi-licensed, the identifiers are
# pipe-separated ("|"). If there is additional data, it follows, separated by
# an underscore. Tags must be unique in the structure.
# 
# For each block, 'match' is a regexp which identifies that license or
# license family uniquely, when matched against a large runon string of the
# entire comment. 'subs' is a set of sub-flavours of that license. Once a type
# is detected, matches are run against the 'match' member of all the subs. If
# none are detected, you have the base flavour; otherwise you have the
# sub-flavour. This can happen recursively (see 'BSD-2-Clause').
#
# 'match' is designed to work with single-line strings of comment data
# where comment chars have been removed and whitespace has been collapsed.
# The matches are case-sensitive, so your regexps will need to accommodate
# that. The top-level ones are the most performance-critical, so do not use
# expensive constructs.
#
# Once a block has been identified as containing a particular license, you
# search from the start for a line matching 'start', and from the end
# for a line matching 'end', and take all the text in between. These are
# matched against individual *unmodified* license lines. 'start' and 'end'
# are both inherited; if a license definition doesn't have them, the ones from
# the parent are used. At the top level, if there is no 'start' or 'end', the
# value of 'match' is used. These defaults attempt to avoid repetition and
# keep the structure simple.
#
# A 'maxlines' entry allows you to give the maximum length for the license
# text; this tries to avoid encompassing two much text when the end-detection
# line could be matched more than once (e.g. in files which have multiple
# license blocks in). If you find the detector is combining licenses, set a
# 'maxlines' value for the first of the two.
#
# A 'cancels' entry allows you to eliminate false positives. If you match a tag
# T, then any tags listed in T's 'cancels' entry will be removed from the final
# set. This allows you to eliminate false positives.
#
# The above algorithms are implemented by detector.py.
###############################################################################

license_data = {

###############################################################################
# MPL
###############################################################################
'MPL-1.1': {
    'start':  r"The contents of this (file|package) are subject to the",
    'match':  r"subject to the Mozilla Public License Version 1.1",
    'end':    r"Contributor|All Rights Reserved|Initial Developer",
    'subs': {
        'MPL-1.1|GPL-2.0+|LGPL-2.1+': { # Mozilla
            'match':  r"either the GNU General",
            'end':    r"terms of any one of the MPL, the GPL or the LGPL"
        },            
        'MPL-1.1|GPL-2.0': {
            'match':  r"GNU( General)? Public License version 2 \(the \"GPL\"\), in",
            'end':    r"either the MPL or the GPL"
        },            
    }
},
'MPL-2.0': {
    'start':  r"Source Code Form [Ii]s subject to the terms of the Mozilla",
    'match':  r"Mozilla Public License,? (v\. |Version )2\.0",
    'end':    r"You can obtain one at http://mozilla\.org/MPL/2\.0/",
    'subs': {
        'MPL-2.0_full-text': {
            'start':  r"Mozilla Public License Version 2\.0",
            'match':  r"each individual or legal entity",
            'end':    r"by the Mozilla Public License, v\. 2\.0",
            'cancels': ['MPL-2.0-no-copyleft-exception', 'LGPL-2.1']
        },            
        'MPL-2.0-no-copyleft-exception': {
            'match':  r"Incompatible With Secondary Licenses",
            'end':    r"by the Mozilla Public License, v\. 2\.0"
        },            
    }
},
###############################################################################
# GPL
###############################################################################
'GPL-1.0+': {
    'start':  r"is free software" + \
              r"|This software is licensed under the terms of the GNU" + \
              r"|This program can be redistributed or modified",
    'match':  r"GNU General Public License",
    'end':    r"along with this program" + \
              r"|gnu\.org/licenses/" + \
              r"|021(10|11|39).*USA" + \
              r"|for more details" + \
              r"|any later version" + \
              r"|Free Software Foundation",
    'subs': {
        'GPL-2.0': {
            'match':  r"Foundation; (either )?version 2",
            'subs': {
                'GPL-2.0+': {
                    'match':  r"any later version",
                    'subs': {
                        'GPL-2.0+-with-libtool-exception': {
                            'match':  r"GNU Libtool",
                        },
                        'Ignore_LGPL-2.1+|MPL-1.1|GPL-2.0+': {
                            'match':  r"Alternatively, the contents of this file"
                        }
                    }
                },
                'GPL-2.0|GPL-3.0': {
                    'start':  r"is free software[:;] you can redistribute it|This file is part of the",
                    'match':  r"version 3(;| dated)",
                    'end':    r"along with this program|gnu\.org/licenses/|0211[01].*USA"
                },
                'GPL-2.0-with-autoconf-exception_1': {
                    'match':  r"configuration script generated by Autoconf",
                    'end':    r"rest of that program"
                },
                'GPL-2.0-with-texinfo-exception': {
                    'match':  r"when this file is read by TeX",
                    'end':    r"Texinfo was invented"
                },
                'MIT|GPL-2.0': {
                    'start':  r"is free software; you can redistribute it",
                    'match':  r"Permission is hereby granted, free of charge",
                    'end':    r"SOFTWARE"
                },
                'Ignore_MPL-1.1_3': {
                    # False positive for dual license
                    'match':  r"Mozilla Public License",
                },
            },
        },
        'GPL-3.0': {
            'start':  r"is free software[:;] you can redistribute it",
            'match':  r"Foundation; either version 3",
            'end':    r"along with this program|gnu\.org/licenses/|0211[01].*USA",
            'subs': {
                'GPL-3.0-with-autoconf-exception_1': {
                    'match':  r"the output of Autoconf when processing",
                    'end':    r"modified version as well"
                },
                'GPL-3.0-with-autoconf-exception_2': {
                    'match':  r"script generated by Autoconf",
                    'end':    r"of the GNU General Public License, version 3"
                },
                'GPL-3.0-with-GCC-exception': {
                    'match':  r"GCC Runtime Library Exception",
                },
                'GPL-3.0-with-libtool-exception': {
                    'match':  r"GNU Libtool",
                    'end':    r"021(10|11|39).*USA|for more details|any later version"
                },
            }
        },
        'GPL-2.0_3': {
            'start':  r"is free software; you can redistribute it",
            'match':  r"License (v|V|version) ?2 as published by the Free",
            'end':    r"021(10|11|39).*USA|Free Software Foundation",
            'subs': {
                # Version of BSD license not specified
                'BSD|GPL-2.0': {
                    'start':  r"is free software; you can redistribute it",
                    'match':  r"BSD license",
                    'end':    r"See README and COPYING for more details|DAMAGE"
                },
            }
        },
        # Appears with XML tags in :-|
        'OSL-1.1|GPL-2.0': {
            'start':  r"The contents of this file are subject",
            'match':  r"Open Software License version 1.1",
            'end':    r"the OSL or the GPL"
        },
        'GPL-1.0+_3': {
            'start':  r"This software may be used and distributed",
            'match':  r"the GNU General Public License, incorporated",
            'end':    r"reference"
        },
        'GPL-2.0_fileref_2': {
            'start':  r"This source code is licensed under the GNU General Public License",
            'match':  r"This source code is licensed under the GNU General Public License",
            'end':    r"See the file COPYING"
        },
        'GPL-2.0_ref': {
            'start':  r"License terms: GNU General Public License \(GPL\) version 2",
            'match':  r"License terms: GNU General Public License \(GPL\) version 2",
            'end':    r"License terms: GNU General Public License \(GPL\) version 2"
        },
        'GPL-2.0_fileref_3': {
            'start':  r"subject to the terms and conditions of the GNU General Public",
            'match':  r"subject to the terms and conditions of the GNU General Public",
            'end':    r"more details"
        },
        'GPL-2.0_fileref_6': {
            'start':  r"This program is distributed|The full GNU General Public License is included",
            'match':  r"The full GNU General Public License is included",
            'end':    r"file called LICENSE"
        },
        'GPL-2.0_urlref_2': {
            'start':  r"The code contained herein is licensed under the GNU General Public",
            'match':  r"The code contained herein is licensed under the GNU General Public",
            'end':    r"http://www\.gnu\.org/copyleft/gpl\.html"
        },
#        'GPL-2.0-with-autoconf-exception_2': {
#            'start':  r"This (program|file) is free software",
#            'match':  r"configuration script generated by Autoconf",
#            'end':    r"rest of that program",
#            'subs': {
#                'GPL-3.0-with-autoconf-exception_3': {
#                    'start':  r"is free software; you can redistribute it",
#                    'match':  r"version 3 of the License",
#                    'end':    r"GNU General Public License, version 3"
#                },
#            }
#        },
        # This is sometimes in a different comment
        'GPL-1.0+-with-bison-exception': {
            'start':  r"As a special exception, you may",
            'match':  r"of the Bison parser skeleton",
            'end':    r"of Bison"
        },
        'Ignore_MPL-2.0_full': {
            # False positive for the full MPL 2 or tri-license
            'match':  r"Mozilla Foundation is the license steward|Mozilla Public License Version",
        },
    }
},
'GPL-1.0+_1': {
    'match':  r"[Ll]icen[cs]ed under the (GNU/)?GPL\.?($| See)",
},
'GPL-1.0+_2': {
    'start':  r"This file may",
    'match':  r"under the terms of the GNU Public",
    'end':    r"License",
    'subs': {
        'Ignore_MPL-1.1': {
            # False positive for dual license
            'match':  r"Mozilla Public License",
        }
    }
},
'GPL-1.0+_4': {
    'match':  r"Released under the General Public License \(GPL\).",
},
'GPL-2.0_2': {
    'start':  r"is free software; you can redistribute it|This software is licensed under the terms of the GNU",
    'match':  r"2 of the Licence",
    'end':    r"any later version",
},
'GPL-2.0_reiser': {
    # a reference to reiserfs/README means "GPL"
    'match':  r"reiserfs/README",
},
'GPL-2.0_ref_2': {
    'start':  r"This software|License",
    'match':  r"(Subject to|terms of) the GNU Public License, (v\.|[vV]ersion )2",
    'end':    r"reference|License"
},
'GPL-2.0_ref_3': {
    'match':  r"[Rr]eleased under (the )?(terms of the GNU )?GPL\s?v2",
},
'GPL-2.0_ref_4': {
    'match':  r"Licensed under the GPL-2",
},
'GPL-2.0_ref_5': {
    'match':  r"\(As all part of the Linux kernel, this file is GPL\)",
},    
'GPL-2.0_fileref': {
    'match':  r"This program can be distributed under the terms of the GNU GPL",
    'end':    r"See the file COPYING"
},
'GPL-2.0_fileref_4': {
    'match':  r"This work is licensed under the terms of the GNU GPL, version 2",
    'end':    r"top-level directory"
},
'GPL-2.0_fileref_5': {
    'match':  r"GPL v2, can be found in COPYING.",
},
'GPL-2.0_fileref_7': {
    'start':  r"for Linux is distributed under the GNU GENERAL PUBLIC",
    'match':  r"GNU GENERAL PUBLIC LICENSE \(GPL\)",
    'end':    r"for more info"
},
'GPL-2.0_fileref_8': {
    'match':  r"This code is licenced under the GPL version 2.",
    'end':    r"COPYING"
},
'GPL-2.0_fileref_9': {
    'match':  r"For licensing details see kernel-base/COPYING",
},
'GPL-2.0_urlref': {
    'match':  r"Licensed under the GPL \(http://www\.gnu\.org/licenses/gpl.html\) license",
},
'GPL-2.0_ref_6': {
    'match':  r"Licensed under GPLv2",
    'subs': {
        'GPL-2.0+_2': {
            'match': "or later"
        }
    }
},
'GPL-2.0_ref_7': {
    'match':  r"under the terms of the GNUv2 General Public License",
},
# Various files in the kernel have other terms and then a "GPL Licensing Note"
# which explains why GPLing it is actually OK.
'GPL-2.0_umbrella': {
    'match':  r"GPL [Ll]icensing [Nn]ote",
},
# Yes, this is a "+" because the actual GPL boilerplate at the end says +.
'BSD-3-Clause|GPL-2.0+': {
    'match':  r"both the GPL version 2 and BSD licenses",
    'end':    r"end of this file",
},
###############################################################################
# LGPL
###############################################################################
'LGPL-1.0+': {
    'start':  r"This file (may|can)|is free software; you can redistribute it",
    'match':  r"(Lesser|Library) General Public License|LESSER GENERAL PUBLIC",
    'end':    r"General Public License|021(10|11|39).*USA|lgpl\.html|Free Software Foundation|of the License",
    'subs': {
        'LGPL-2.1': {
            'match':  r"[Vv]ersion 2",
            'subs': {
                'LGPL-2.1_2': {
                    'match':  r"2\.1 of the GNU Lesser General Public License",
                    'end':    r"A PARTICULAR PURPOSE",
                },
                'LGPL-2.1_full': {
                    'start':  r"GNU LESSER GENERAL PUBLIC LICENSE",
                    'match':  r"designed to take away",
                    'end':    r"That's all there is to it|DAMAGES",
                    'cancels': ['GPL-2.0+']
                },
                'LGPL-2.1+|MPL-1.1|GPL-2.0+': {
                    'match':  r"Alternatively, the.*Mozilla Public License",
                    'end':    r"\(at your option\) any later version"
                },
                'LGPL-2.1|MPL-1.1': { # Cairo
                    'match':  r"should have received a copy of the MPL along with",
                    'end':    r"governing rights and limitations",
                    'cancels': ['MPL-1.1']
                },
                'Ignore_MPL-1.1|GPL-2.0+|LGPL-2.1+': {
                    # False positive for tri-license
                    'match':  r"Alternatively, the contents of this file may be used",
                }
            }
        },
        'Ignore_MPL-1.1_2': {
            # False positive for dual license
            'match':  r"Mozilla Public License",
        }
    }
},
'LGPL-1.0+_ref': {
    'match':  r"This file is released under the LGPL\.?$",
},
'LGPL_glib_lookelsewhere': {
    # glib license is LGPL
    'match': r"This file is distributed under the same license as the glib package",
},
###############################################################################
# Apache
###############################################################################
'Apache-2.0_urlref': {
    'match':  r"http://www.apache.org/licenses/LICENSE-2\.0",
    'subs': {
        'Apache-2.0': {
            'start':  r"Licensed under the Apache License,? Version 2\.0" + \
                      r"|Licensed to the Apache Software Foundation \(ASF\)",
            'match':  r"under the Apache License,? Version 2\.0",
            'end':    r"the License\.?|licenses/LICENSE-2\.0",
            'maxlines': 12
        },
    }
},        
'Apache-2.0_fulltext': {
    'start':  r"Apache License",
    'match':  r"\"Legal Entity\" shall mean the union of the acting",
    'end':    r"warranty or additional liability",
    'maxlines': 12
},
'Apache-2.0_fileref': {
    'match':  r"Use of this source code is governed by the Apache License, Version 2\.0",
    'end':    r"See the COPYING file for details"
},
###############################################################################
# HPND
###############################################################################
'HPND_no-repro-required': {
    'start':  r"[Pp]ermission to use, copy, modify",
    'match':  r"[Pp]ermission to use, copy, modify,?(?: and(/or)?)? distribute",
    'end':    r"SOFTWARE|express or implied|without fee|of any kind" + \
              r"|written prior permission|supporting documentation" + \
              r"|MODIFICATIONS|prior written authorization|DERIVATIVE WORK" + \
              r"|implied warranty|is preserved",
    'subs': {
        'HPND': {
            'match':  r"all copies|notice is preserved",
        },
#        'HPND_2': {
#            'match':  r"freely granted",
#            'end':    r"is preserved",
#        },
        'HPND_SunRPCGSS': {
            'start':  r"Export of this software",
            'match':  r"WITHIN THAT CONSTRAINT, permission to use",
            'end':    r"A PARTICULAR PURPOSE"
        },
        'HPND_Coda': {
            'match':  r"CODA IS AN EXPERIMENTAL SOFTWARE SYSTEM",
            'end':    r"DERIVATIVE WORK"
        },
    }
},
'HPND_3': {
    'match':  r"Permission to copy, use, modify, sell and distribute",
    'end':    r"suitability for any purpose",
},
'HPND_4': {
    'start':  r"Permission is granted to use, copy",
    'match':  r"create derivative works and redistribute",
    'end':    r"DAMAGES",
},
'HPND_Motorola': {
    'start':  r"THE SOFTWARE is provided",
    'match':  r"granted a copyright license to use, modify",
    'end':    r"of Motorola, Inc.",
},
###############################################################################
# MIT
###############################################################################
'MIT': {
    'start':  r"Permission is hereby granted, " + \
              r"(?:free of charge|without written agreement)" + \
              r"|licensed under the MIT",
    'match':  r"Permission is hereby granted, " + \
              r"(?:free of charge|without written agreement)" + \
              r"|licensed under the MIT",
    'end':    r"SOFTWARE|copyright holder|OR MODIFICATIONS|MATERIALS",
    'subs': {
        'MIT|GPL-2.0_urlref': { # jQuery
            'start': r"Dual licensed under the MIT",
            'match': r"Dual licensed under the MIT (and|or) GPL",
            'end':   r"jquery\.(com|org)/[Ll]icense|licenses\."
        },
        'MIT|GPL-2.0_fileref': { # jQuery
            'start': r"Dual licensed under the MIT",
            'match': r"Dual licensed under the MIT \(MIT-LICENSE.txt\) and GPL",
            'end':   r"licenses"
        },
        'MIT_BSD_hybrid': {
            'match': r"Redistributions? in binary form",
        },
        'BSL-1.0': {
            'start': r"Boost Software License",
            'match': r"Boost Software License",
        },
        'MIT_Crockford': {
            'match': r"The Software shall be used for Good, not Evil",
        },
        'MIT_UIllinois': {
            'start': r"This file is dual licensed",
            'match': r"University of Illinois Open",
            'end':   r"for details",
            'cancels': ['MIT_BSD_hybrid']
        },
        # OFL has MIT-like language, so is a false positive
        'Ignore_OFL-1.1_2': {
            'match':  r"SIL Open Font License, Version 1\.[1|0]",
        },
    }
},
'MIT_fileref': {
    'start':  r"This is free software.*distribute,? or modify",
    'match':  r"terms of the MIT/X [lL]icense",
    'end':    r"terms of the MIT/X [lL]icense|with this distribution",
},
'MIT_urlref': {
    'match':  r"Some rights reserved: http://opensource.org/licenses/mit",
},
'MIT_urlref_2': {
    'match':  r"MIT License - http://opensource.org/licenses/mit-license\.php",
},
'MIT_ref': {
    'match':  r"under (an |the )?MIT license",
    'end':    r"http://opensource.org/licenses/MIT|under (an|the )?MIT license",
    'subs': {
        'MIT_Lodash_urlref': {
            'start': r"Available under MIT license",
            'match': r"lodash.com/license",
            'end':   r"Available under MIT license"
        },
        'MIT_codemirror_urlref': {
            'match': r"codemirror\.net/LICENSE",
            'end':   r"LICENSE"
        },
    }
},
'MIT_ref2': {
    'match':  r"MIT Licensed",
},
'MIT|BSD-3-Clause_alameda': {
    'match':  r"Available via the MIT or new BSD license",
    'end':    r"http://github\.com/requirejs/alameda",
},
'BSL-1.0_urlref': {
    'match':  r"Distributed under the Boost Software License, Version 1\.0",
    'end':    r"http://www\.boost\.org/LICENSE_1_0\.txt",
},
###############################################################################
# BSD
###############################################################################
'BSD-2-Clause': {
    'match':  r"Redistribution and use of this software" + \
              r"|[Rr]edistribution and use in source and",
    'end':    r"DAMAGE|PURPOSE",
    'subs': {
        'BSD-3-Clause': {
            'match':  r"name.*(may|must) not be used to" + \
                      r"|Neither the (author|name).*may be used to" + \
                      r"|The name of the company nor the name of the author",
            'subs': {
                'BSD-4-Clause': {
                    'match':  r"advertising materials",
                    'subs': {
                        # The 4th clause is not a problem because it has been
                        # waived permanently
                        'BSD-4-Clause_UC': {
                            'match':  r"University of California",
                        },
                        'BSD-4-Clause_NetBSD': {
                            'match':  r"The NetBSD Foundation",
                        },
                        # Waived for Mozilla code
                        'BSD-4-Clause_RTFM': {
                            'match':  r"RTFM, Inc",
                        },
                        # This one, there is no waiver but we aren't using
                        # the code, even though the Android people have
                        # copied the notice into a NOTICE file we read.
                        # So we detect it separately so we can ignore it.
                        'BSD-4-Clause_Winning': {
                            'match':  r"Winning Strategies, Inc",
                        },
                    }
                },
                'BSD|GPL-1.0+': {
                    'match':   r"General Public License",
                    'end':     r"DAMAGE|damage|IN ANY WAY",
                    'cancels': ['GPL-1.0+']
                }
            }
        },
#        'BSD-4-Clause_Compact': {
#            'match':  r"in all such forms.*advertising materials",
#            'subs': {
#                'BSD-4-Clause_Compact_UC': {
#                    'match':  r"University of California,( Lawrence)? Berkeley",
#                },
#            }
#        },
        'BSD-4-Clause_SSLeay': {
            'match':  r"Eric Young|Tim Hudson",
        },
        'Permissive_6': {
            'match':  r"provided that redistributions of source",
            'end':    r"modification",
        },
        'Ignore_PD_Peslyak': {
            'match':  r"Alexander Peslyak in 2001",
        }
    }
},
'BSD_fileref': {
    'start':  r"Use of this",
    'match':  r"source code is governed by a BSD-style",
    'end':    r"LICENSE|source tree|PATENTS"
},
'BSD_fileref2': {
    'match':  r"BSD, see LICENSE for details",
},
'BSD_fileref3': {
    'match': r"This software may be distributed under the terms of the BSD license",
    'end':   r"See README for more details"
},
'BSD-3-Clause_fileref_xiph': {
    'start': r"USE, DISTRIBUTION AND REPRODUCTION",
    'match': r"BSD-STYLE SOURCE LICENSE INCLUDED WITH",
    'end':   r"TERMS BEFORE DISTRIBUTING"
},
'BSD-2-Clause_urlref': {
    'match': r"The program is distributed under terms of BSD",
    'end':   r"licenses/bsd-license\.php"
},
'BSD-3-Clause_urlref': {
    'match': r"Licensed under the New BSD license",
    'end':   r"licenses/BSD-3-Clause"
},
'BSD-3-Clause_urlref_yui': {
    'start': r"Code licensed under the BSD License",
    'match': r"http://developer\.yahoo\.com/yui/license\.html",
},
'BSD-3-Clause_urlref_paj': {
    'start': r"Distributed under the BSD License",
    'match': r"See http://pajhome\.org\.uk/crypt/md5 for",
    'end':   r"http://pajhome\.org\.uk/crypt/md5 for"
},
'BSD-3-Clause_urlref_voidspace': {
    'start': r"This software is licensed under the terms of the BSD license",
    'match': r"http://www\.voidspace\.org\.uk/python/license.shtml",
},  
'BSD-3-Clause_EDL_urlref': {
    'start': r"This program and the accompanying materials",
    'match': r"http://www\.eclipse\.org/org/documents/edl-v10\.html",
},
'BSD-Protection': {
    'match': r"BSD PROTECTION LICENSE",
    'end':   r"OF SUCH DAMAGES"
},
'BSD-like_editline': {
    'start': r"Permission is granted to anyone to use this",
    'match': r"no matter how awful",
    'end':   r"removed or altered",
},
###############################################################################
# Generic filerefs (i.e. filename does not define license)
###############################################################################
'COPYING_fileref': {
    'match':  r"See the file COPYING for copying permission",
},
'COPYING_fileref2': {
    'start':  r"COPYING for licensing terms",
    'match':  r"See (\.\./)*COPYING for licensing terms",
    'end':    r"COPYING for licensing terms"
},
'COPYRIGHT_fileref': {
    'match':  r"See the accompanying file \"COPYRIGHT\" for",
    'end':    r"NO WARRANTY FOR THIS SOFTWARE"
},
'LICENSE_fileref': {
    'match':  r"See LICENSE for copying information",
},
'po_fileref': {
    'match':  r"This file is distributed under the same license as the .{0,20} package.",
},
'README_fileref': {
    'start':  r"For details on the license",
    'match':  r"file, README, in this same",
    'end':    r"file, README, in this same"
},
'LICENSE.txt_fileref': {
    'match':  r"See LICENSE.txt for license details"
},
###############################################################################
# Permissive
#
# "Permissive" licenses are those which do not have text reproduction
# requirements
###############################################################################
'Permissive_GNU1': {
    'match':  r"Copying and distribution of this file, with or without",
    'end':    r"notice are preserved"
},
'Permissive_GNU2': {
    'start':  r"This (?:Makefile\.in|file) is free software",
    'match':  r"This (Makefile\.in|file) is free software.*with or without modifications",
    'end':    r"PARTICULAR PURPOSE|notice is preserved",
    'maxlines': 10
},
'Permissive_1': {
    'match':  r"This software is provided \"as is\"; redistribution and",
    'end':    r"possibility of such damage" 
},
'Permissive_2': {
    'match':  r"This material is provided \"as is\", with absolutely no",
    'end':    r"above copyright notice" 
},
'Permissive_3': {
    'start':  r"You may redistribute unmodified or modified versions",
    'match':  r"I shall in no event be liable",
    'end':    r"using this software" 
},
'Permissive_4': {
    'start':  r"You may use this program",
    'match':  r"as desired without restriction",
},
'Permissive_5': {
    'start':  r"You may use, copy, modify and distribute this code",
    'match':  r"use\) and without fee",
    'end':    r"this code" 
},
'Permissive_ACE': {
    'start':  r"ACE\(TM\), TAO\(TM\), CIAO\(TM\)",
    'match':  r"built using DOC software",
    'end':    r"their names" 
},
###############################################################################
# Other Non-Copyleft
###############################################################################
'AFL-2.1': {
    'match':  r"Licensed under the Academic Free License version 2.1",
},
'ICU': {
    'start':  r"This software is made|ICU License",
    'match':  r"ICU License --? ICU",
    'end':    r"respective owners|and later"
},
'BSD-3-Clause_JPNIC': {
    'start':  r"The following License Terms and Conditions apply",
    'match':  r"The name of JPNIC may not be used",
    'end':    r"POSSIBILITY OF SUCH DAMAGES"
},    
'ISC_fileref': {
    'match':  r"This program is made available under an ISC-style license",
    'end':    r"file LICENSE for details"
},
'SGI-B-1.1': {
    'start': r"License Applicability",
    'match': r"SGI Free Software License B, Version 1.1",
    'end':   r"NON-INFRINGEMENT"
},
'SGI-B-2.0': {
    'start': r"SGI Free Software B License",
    'match': r"SGI Free Software B License Version 2\.0",
    'end':   r"oss\.sgi\.com/projects/FreeB/"
},
'NVidia': {
    'match': r"NVIDIA Corporation\(\"NVIDIA\"\) supplies this software to you",
    'end':   r"OF SUCH DAMAGE"
},
'FTL': {
    'start': r"This software, and all works of authorship",
    'match': r"distributed under the FreeType Project License",
    'end':   r"and you accept them fully"
},
'FTL_fileref': {
    'match': r"This file is part of the FreeType project" + \
             r"|under the terms of the FreeType project license",
    'end':   r"fully"
},
'FTL_fulltext': {
    'match': r"The FreeType Project LICENSE",
    'end':   r"http://www\.freetype\.org"
},
'W3C_urlref': {
    'match': r"(program|work) is distributed under the W3C('s|\(r\)) Software" + \
             r"|The following software licensing rules apply",
    'end':   r"A PARTICULAR PURPOSE|for more details|copyright-software"
},
'WebM_urlref': {
    'match':  r"This code is licensed under the same terms as WebM",
    'end':    r"Additional IP Rights Grant|Software License Agreement"
},
'WHATWG': {
    'start': r"You are granted a license to use",
    'match': r"use, reproduce and create derivative works of",
    'end':   r"this document"
},
'Zlib_ref': {
    'match': r"Licensed under the zlib/libpng license",
},
'Zlib_fileref': {
    'start': r"For conditions of distribution and use, see copyright notice",
    'match': r"distribution and use, see copyright notice in zlib.h",
    'end':   r"notice in zlib.h"
},
'bzip2-1.0.6_fileref': {
    'start': r"This program is released under the terms",
    'match': r"This program is released under the terms of the license contained in the file LICENSE.",
    'end':   r"the file LICENSE"
},
'jsimdext_fileref': {
    'match': r"For conditions of distribution and use, see copyright notice in jsimdext\.inc",
},
'Python-2.0': {
    'start': r"This module is free software, and you",
    'match': r"same terms as Python itself",
    'end':   r"OR MODIFICATIONS"
},
'CDDL-1.0': {
    'start': r"The contents of this file are subject",
    'match': r"Common Development and Distribution License",
    'end':   r"under the License"
},
'Libpng': {
    'match': r"The PNG Reference Library is supplied",
    'end':   r"appreciated"
},
'Libpng_fileref': {
    'match': r"This (code|document) is released under the libpng license",
    'end':   r"under the libpng license|license in png.h"
},
'curl_urlref': {
    'start': r"This software is licensed as described",
    'match': r"http://curl\.haxx\.se/docs/copyright\.html",
    'end':   r"either express or implied"
},
'IJG_fileref': {
    'match': r"part of the Independent JPEG Group's software",
    'end':   r"accompanying README file"
},
'IJG': {
    'start': r"The authors make NO WARRANTY or representation",
    'match': r"for the use of any IJG author's name",
    'end':   r"by the product vendor"
},
'Zlib': {
    'start': r"This software is provided 'as-is'",
    'match': r"use this software for any purpose, including commercial applications",
    'end':   r"any source distribution"
},
'MirOS': {
    'start': r"Provided that these terms and disclaimer and all",
    'match': r"immediate fault when using",
    'end':   r"using the work as intended"
},  
'NAIST': {
    'start': r"Use, reproduction, and distribution of this software",
    'match': r"in no event shall NAIST be liable",
    'end':   r"program is concerned"
},  
'Mozilla_lookelsewhere': {
    'match': r"Please see the file toolkit/content/license\.html",
    'end':   r"name or logo|licensing\.html"
},
'Unicode-TOU_urlref': {
    'match': r"For terms of use, see http://www\.unicode\.org/terms_of_use\.html",
},
'OpenSSL_ref': {
    'start': r"Rights for redistribution|The OpenSSL Project",
    'match': r"according to the OpenSSL license",
},
# This is a non-free license but it got changed by Sun:
# http://spot.livejournal.com/315383.html
'SunRPC': {
    'start': r"Sun RPC is a product of Sun Microsystems, Inc",
    'match': r"copy or modify Sun RPC without charge",
    'end':   r"possibility of such damages"
},    
###############################################################################
# OFL
###############################################################################
'OFL-1.0': {
    'start':  r"This Font Software is licensed",
    'match':  r"SIL Open Font License, Version 1\.0",
    'end':    r"IN THE FONT SOFTWARE"
},
'OFL-1.1': {
    'start':  r"This Font Software is licensed",
    'match':  r"SIL Open Font License, Version 1\.1",
    'end':    r"IN THE FONT SOFTWARE"
},
'OFL-1.1_ref': {
    'start':  r"Licensed under the SIL",
    'match':  r"SIL Open Font License 1.1 \(see file",
    'end':    r"OFL.txt"
},
###############################################################################
# EPL
###############################################################################
'EPL-1.0': {
    'match': r"Licensed under the Eclipse Public License, Version 1\.0",
    'end':   r"under the License"
},  
'EPL-1.0_fulltext': {
    'start': r"Eclipse Public License - v 1\.0",
    'match': r"The Eclipse Foundation is the initial Agreement Steward",
    'end':   r"any resulting litigation"
},
###############################################################################
# CPL
###############################################################################
'CPL-1.0': {
    'start': r"THE ACCOMPANYING PROGRAM|DEFINITIONS",
    'match': r"COMMON PUBLIC LICENSE",
    'end':   r"any resulting litigation"
},
###############################################################################
# CC (could expand this to capture version)
###############################################################################
'CC-BY': {
    'match': r"Creative Commons Attribution \d\.\d",
},    
###############################################################################
# Public Domain
###############################################################################
'PD': {
    'match': r"[Pp]ublic [Dd]omain|PUBLIC DOMAIN",
    'end':   r"[Pp]ublic [Dd]omain|PUBLIC DOMAIN|conceived",
    'subs': {
        'CC0-1.0': {
            'start': r"Any copyright is dedicated to the Public Domain" + \
                      "|http://creativecommons\.org/(publicdomain/zero/1\.0|licenses/publicdomain)",
            'match': r"Any copyright is dedicated to the Public Domain" + \
                      "|http://creativecommons\.org/(publicdomain/zero/1\.0|licenses/publicdomain)",
            'end':   r"http://creativecommons\.org/(publicdomain/zero/1\.0|licenses/publicdomain)"
        },
        'PD_Peslyak': {
            'start': r"This software was written by Alexander",
            'match': r"This software was written by Alexander Peslyak",
            'end':   r"express or implied"
        }
    }
},
'PD_no-copyrightable-info': {
    'start': r"This header was automatically generated from",
    'match': r"no copyrightable information",
},
'PD_not-copyrightable': {
    'match': r"Not copyrightable",
},
'PD_sqlite-blessing': {
    'start': r"The author disclaims copyright",
    'match': r"In place of a legal notice, here is a blessing",
    'end':   r"taking more than you give"
},
'PD_explicitly-no-copyright': {
    'match': r"Explicitly no copyright\.",
},
###############################################################################
# Proprietary
###############################################################################
'proprietary_IBM': {
    'start': r"International Business Machines",
    'match': r"(International Business Machines|IBM) Corporation and others\.\s+All [Rr]ights [Rr]eserved",
},
'proprietary_IBM_purify': {
    'start': r"IBM Corporation",
    'match': r"All Rights Reserved. You may recompile and redistribute these definitions as required.",
    'end':   r"as required"
},
'proprietary_Unicode': {
    'match': r"This source code is provided as is by Unicode, Inc",
    'end':   r"remains attached"
},
'proprietary_Microsoft': {
    'start': r"This license governs use of code marked",
    'match': r"Microsoft Windows operating system product",
    'maxlines': 80
},
'proprietary_Broadcom_2': {
    'match': r"UNPUBLISHED PROPRIETARY SOURCE CODE of Broadcom",
    'end':   r"permission of Broadcom Corporation"
},
'confidential': {
    'match': r"[Cc]onfidential",
    'subs': {    
        'proprietary_TCL': {
            'start': r"This material is company confidential",
            'match': r"permission of TCL Communication",
            'end':   r"Limited"
        },
        'proprietary_Broadcom': {
            'match': r"Broadcom.*Proprietary and confidential.",
        },
    }
},

}
