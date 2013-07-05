###############################################################################
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Configuration for relic
###############################################################################

import re
import os

config_cache = {}

def get_config(structname, treename):
    cache_key = treename + "|" + structname
    
    if cache_key not in config_cache:    
        struct = globals()["_g_" + structname]
        config = struct.get('_common')
        config.extend(struct.get(treename, []))
        config_cache[cache_key] = config
    
    return config_cache[cache_key]


# Returns comment delimiters for this filename, or None if we can't work it out
def get_delims(filename):
    delims = None
    xfilename = get_true_filename(filename)
    
    # special cases for some basenames
    basename = os.path.basename(xfilename)
    try:
        delims = _g_basename_to_comment[basename]
    except KeyError:
        pass
    if not delims: # use the file extension
        ext = os.path.splitext(xfilename)[1]
        try:
            delims = _g_ext_to_comment[ext]
        except KeyError:
            pass
    if not delims: # try to use the shebang line, if any
        fin = open(filename, 'r')
        firstline = fin.readline()
        fin.close()
        if firstline.startswith("#!"):
            for pattern, cds in _g_shebang_pattern_to_comment:
                if pattern.match(firstline):
                    delims = cds
                    break

    return delims


def get_true_filename(filename):
    splitname = os.path.splitext(filename)
    if splitname[1] in _g_strip_exts:
        # Strip extensions which hide the real extension. E.g. 
        # "<foo>.in" is generally a precursor for a filetype
        # identifiable without the ".in". Drop it.
        return splitname[0]
    else:
        return filename

###############################################################################
# Configuration lists
###############################################################################

# Extensions to strip off to reveal the "real" extension
_g_strip_exts = [".in", ".dist"]


# Extensions to skip
# List includes binary extensions in case binary checking is turned off
_g_skip_exts = {
  '_common' :
      [".mdp", ".order", ".dsp", ".dsw", ".json", ".webapp", ".sln",
       ".png", ".jpg", ".jpeg", ".gif", ".tiff", ".rtf",
       ".pbxproj", ".pch", ".pem", ".icns", ".patch", ".diff",
       ".dic_delta", ".dic"],
}


# Extensions not to add a license to when they don't have one (due to
# inappropriateness or comment character confusion)
_g_skip_add_exts = {
  '_common': 
    [".txt", ".TXT", ".inc", ".s", ".manifest", ".map", ".dat"],
}


# Filenames to always skip, wherever they are found
_g_skip_file_basenames = {
  '_common': [
    # Used by various SCMs
    ".cvsignore",
    ".gitignore",
    ".gitattributes",
    ".hgignore",
    ".hgtags",
    ".bzrignore",
    
    # Auto-generated from other files
    "configure",

    # license and readme files
    "README",
    "readme",
    "ReadMe",
    "README.txt",
    "README.md",
    "AUTHORS",
    "NEWS",
    "TODO",
    "ChangeLog",
  ],
   
  'mozilla-central': [
    # license and readme files
    "LICENSE",
    "license",
    "LICENSE-MPL",
    "LEGAL",
    "copyright",

    ".mozconfig",
    "ignore-me",

    # GPL with autoconf exception
    "config.guess",
    "config.sub",
    "aclocal.m4",

    "AndroidManifest.xml.in",
    
    # Catted into makefiles; can't have a header
    "android-resources.mn",
    
    # Don't know comment char; always short
    "module.ver",
  ],
  
  'comm-central': [
    # Don't know comment char; always short
    "module.ver",  
  ],

  'mcs': [
    "jquery.domec.min-0.3.1.js",
  ],

  'b2g': [
    "Android.mk", # Loads of them, seemingly none without a license header
  ],
}


# Directories to always skip, wherever they are found
_g_skip_dir_basenames = {
  '_common': [
    "CVS",
    ".hg",
    ".git",
    ".bzr",
    ".repo",
  ],

  'b2g': [
    "NOTICE_FILES",
    "toolchain", 

    # Not shipping tests
    "mochitest",
    "reftest",
    "reftests",
    "crashtest",
    "crashtests",
    "test",
    "tests",
    "jsreftest",
    "imptests",
    "testsuite",
    "examples",

    "contrib",
    "doc",
  ],
}


# Directories to always skip when adding, wherever they are found
_g_skip_add_dir_basenames = {
  '_common': [
  ],
  
  'mozilla-central': [
    # Not relicensing m-c tests, as things break too often
    "mochitest",
    "reftest",
    "reftests",
    "crashtest",
    "crashtests",
    "test",
    "tests",
    "jsreftest",
    "imptests",
  ],
}


# Individual files to skip
_g_skip_files = {
  '_common': [
  ],
  
  'mozilla-central': [
    # Files containing copies of licence text which confuses the script
    "gfx/cairo/cairo/COPYING-LGPL-2.1",
    "gfx/cairo/cairo/COPYING-MPL-1.1",
    
    # Files containing global licensing information
    "toolkit/content/license.html",
    
    # GPLed build tools
    "intl/uconv/tools/parse-mozilla-encoding-table.pl",
    "intl/uconv/tools/gen-big5hkscs-2001-mozilla.pl",
    
    # GPL with autoconf exception (same license as files distributed with)
    "build/autoconf/codeset.m4",
    "security/svrcore/depcomp",
    "security/svrcore/compile",
    "security/svrcore/missing",
    "security/svrcore/ltmain.sh",
    
    # Public domain or equivalent
    "nsprpub/config/nspr.m4",
    "security/nss/lib/freebl/mpi/mp_comba_amd64_sun.s",
    
    # GSSAPI has BSD-like licence requiring some attribution
    "extensions/auth/gssapi.h",

    # Catted into makefiles; can't have a header
    "mobile/android/sync/android-drawable-resources.mn",
    "mobile/android/sync/android-drawable-ldpi-resources.mn",
    "mobile/android/sync/preprocess-sources.mn",
    "mobile/android/sync/java-third-party-sources.mn",
    "mobile/android/sync/android-values-resources.mn",
    "mobile/android/sync/android-drawable-hdpi-resources.mn",
    "mobile/android/sync/java-sources.mn",
    "mobile/android/sync/android-layout-resources.mn",
    "mobile/android/sync/android-drawable-mdpi-resources.mn",
    
    # Catted in other ways
    "mobile/android/sync/manifests/SyncAndroidManifest_activities.xml.in",
    "mobile/android/sync/manifests/SyncAndroidManifest_permissions.xml.in",
    "mobile/android/sync/manifests/SyncAndroidManifest_services.xml.in",    
    
    # GPLed tools
    "toolkit/crashreporter/client/certdata2pem.py",
    "js/src/vm/make_unicode.py",
    
    # MPL 2, but too many license blocks too close to the top of file
    # and filename does not begin with "gen".
    "intl/chardet/tools/charfreqtostat.pl",
    
    # BSD
    "xpcom/glue/nsQuickSort.cpp",
    
    # Sample file
    "config/tests/src-simple/thesrcdir/preproc.in",
    
    # README
    "extensions/spellcheck/locales/en-US/hunspell/README_en_US.txt",
    "intl/locales/en-US/hyphenation/README_hyph_en_US.txt",
    
    # WHATWG
    "content/xml/content/src/htmlmathml-f.ent",
    
    "config/configobj.py", # BSD
    
    "dom/imptests/WebIDLParser.js", # MIT
    "dom/imptests/idlharness.js", # BSD
    "dom/imptests/testharness.js", # BSD
    
    "gfx/tests/gfxColorManagementTest.cpp", # "do anything"
    
    "intl/lwbrk/src/rulebrk.h", # liberal, MIT-like
    "intl/lwbrk/src/th_char.h", 
  ],

  'comm_central': [
  ],

  'addon_sdk': [
    # Addon SDK
    "doc/static-files/js/jquery.js", # MIT/GPL
    "examples/annotator/data/jquery-1.4.2.min.js", # MIT/GPL
    "examples/reddit-panel/data/jquery-1.4.4.min.js", # MIT/GPL
  ],

  'camino': [
    # Camino
    "src/extensions/ImageAndTextCell.m", # Apple BSD-like
    "src/extensions/ImageAndTextCell.h", # Apple BSD-like
    "src/extensions/MAAttachedWindow.m", # Matt Gemmill's copy of the above lic
    "src/extensions/MAAttachedWindow.h", # Matt Gemmill's copy of the above lic
    "IBPalette/resources/palette.table",
    "src/spotlight-importer/Importer-main.c",
  ],

  'browserid': [
    # BrowserID
    "resources/static/test/qunit.css", # MIT
  ],
  
  'instantbird': [
    # Must start with a newline; are appended to other files
    "instantbird/installer/windows/nsis/updater_append.ini",
    "instantbird/locales/updater_append.ini",
    
    # JSON data with wrong extension
    "instantbird/themes/smileys/theme.js",
  ],
  
  'bedrock': [
    "templates/includes/webtrends.html", # Copyright WebTrends
    "media/js/firefox/technology/dsp.js", # MIT
    "media/js/less-1.2.1.min.js", # Apache
    "media/css/sandstone/mixins.less", # CC-BY
    "media/js/firefox/technology/beatdetektor.js", # LGPL 3.0
    "media/js/firefox/technology/main.js", # minified
  ],

  'b2g': [
    # Random GPLv3 helper script which we aren't shipping
    "gecko/js/src/vm/make_unicode.py",

    # Random LGPLed Symbian file
    "gecko/js/src/assembler/jit/ExecutableAllocatorSymbian.cpp",

    # Solaris only
    "gecko/media/libsydneyaudio/src/sydney_audio_sunaudio.c",
  ],

  'webxray': [
    'static-files/yepnope.1.0.2-min.js',
  ],

  'kuma': [
    'apps/demos/__init__.py',
    'media/js/jquery-1.9.1.js',
    'media/js/html5.js',
    "media/js/mdn/jquery.hoverIntent.minified.js",
  ],
} # _g_skip_files


# Individual directories to skip
_g_skip_dirs = {
  '_common': [
  ],
  
  'bedrock': [
    "vendor-local",
    "media/js/libs",
    # OpenSans is Apache-licensed, but FontSquirrel puts in bogus stuff
    "media/fonts",
  ],
  
  'mozilla_central': [
    "security/nss",
    "security/coreconf",
    "nsprpub",

    # BSD-licensed
    "dbm",
    
    "other-licenses",
    
    "browser/devtools/highlighter/", # BSD
    "browser/devtools/sourceeditor/orion", # EPL XXXCheck
    "browser/extensions/pdfjs", # MIT
    
    "build/pgo/blueprint", # MIT/GPL
    
    # Other directories we want to exclude
    "embedding/tests",     # Agreed as BSD
    "gfx/cairo",           # LGPL/MPL
    "gfx/graphite2",       # LGPL leading, with MPL and GPL alternatives
    "gfx/angle",           # BSD
    "gfx/harfbuzz",        # Permissive, BSD-like
    "gfx/ots",             # BSD
    "gfx/qcms",            # MIT
    "gfx/skia",            # BSD
    "gfx/ycbcr",           # BSD

    "extensions/spellcheck/hunspell", # MPL/LGPL/GPL, but not ours

    # mkdepend - BSD
    "config/mkdepend",
    "js/src/config/mkdepend",
    "security/coreconf/mkdepend",
    
    "browser/app/profile/extensions/testpilot@labs.mozilla.com/content/flot",
    "build/pgo/js-input", # SunSpider - Apple BSD
    "content/canvas/test/webgl", # WebGL test suite - BSD
    "db/sqlite3", # Public Domain
    
    "dom/plugins/test/testplugin", # BSD
    "dom/tests/mochitest/ajax", # Various Ajax libraries, all MIT
    "dom/tests/mochitest/dom-level1-core", # W3C
    "dom/tests/mochitest/dom-level2-core", # W3C
    "dom/tests/mochitest/dom-level2-html", # W3C

    "editor/libeditor/html/tests/browserscope/lib/richtext2", # Apache

    "intl/hyphenation", # tri-licensed but prob. not us; Bug 716482
    
    "ipc/chromium/base",   # BSD
    "ipc/chromium/src",    # BSD

    "js/src/assembler/assembler",    # BSD
    "js/src/assembler/jit",          # BSD
    "js/src/assembler/wtf",          # BSD
    "js/src/ctypes/libffi",          # MIT
    "js/src/jit-test/tests/sunspider", # BSD
    "js/src/metrics/jint/sunspider",   # BSD
    "js/src/jit-test/tests/v8-v5",   # BSD
    "js/src/metrics/jint/v8",        # BSD
    "js/src/v8",                     # BSD
    "js/src/v8-dtoa",                # BSD
    "js/src/yarr",                   # BSD

    "media/libjpeg",
    "media/libpng",
    "media/libnestegg", # BSD/ISC
    "media/libogg",     # BSD
    "media/libtheora",  # BSD
    "media/libtremor",  # BSD    
    "media/libvorbis",  # BSD
    "media/libvpx",     # BSD
    "media/libcubeb",   # MIT
    "media/libopus",    # BSD
    "media/libspeex_resampler", # BSD
    
    "memory/jemalloc",  # BSD

    "mfbt/double-conversion", # BSD
    
    "mobile/android/base/apache/commons/codec", # Apache
    "mobile/android/base/httpclientandroidlib", # Apache
    "mobile/android/base/json-simple",
    
    "modules/freetype2",  # FreeType License
    "modules/libbz2/src", # BSD
    "modules/zlib",
    "security/nss/lib/zlib",

    "parser/expat", # MIT
    "parser/html",  # MIT
    
    "testing/mochitest/MochiKit", # MIT
    "testing/mochitest/tests/MochiKit-1.4.2/MochiKit", # MIT
    "testing/mochitest/pywebsocket", # BSD
    
    "toolkit/components/alerts/mac/growl", # BSD
    "toolkit/crashreporter/google-breakpad", # BSD
    
    "tools/profiler/libunwind", # MIT
  ],

  'camino': [
    # Camino
    "sparkle", # MIT
    "google-breakpad", # BSD
    "growl", # BSD
    "striptease", # APSL build tool
    "flashblock", # Upstream tri-licence
  ],

  'addon_sdk': [
    # Addon SDK
    "python-lib/markdown", # BSD
    "python-lib/simplejson", # MIT
    "doc/static-files/syntaxhighlighter", # MIT/GPL dual
  ],

  'bugzilla': [
    # Bugzilla
    "lib",
    "data",
    "js/yui",
    "js/history.js", # Yes, this is a directory
  ],

  'browserid': [
    # BrowserID
    "resources/static/lib", # Need to check manually
  ],

  'elmo': [
    # elmo
    "static/simile",
    "static/js/jquery.ui",
    "static/css/jquery.ui",
    "static/js/libs",
    "vendor-local",
  ],

  'socorro': [
    # Socorro
    "puppet",
    "docs",
    "webapp-php/js/jquery",
    "webapp-php/js/flot-0.7",
    "webapp-php/modules/ezcomponents/libraries/Feed",
    "webapp-php/modules/ezcomponents/libraries/Base",
    "webapp-php/modules/flot",
    "webapp-php/modules/forge",
    "webapp-php/system/core",
    "webapp-php/system/i18n",
    "webapp-php/system/views",
    "webapp-php/system/helpers",
    "webapp-php/system/libraries",
  ],

  'comm-central': [
    # comm-central
    "other-licenses",
    "calendar/libical", # MPL/LGPL
    "mozilla",
    "build/pypng",  
    
    "mail/test/resources/virtualenv",
    "mail/test/resources/simplejson-2.1.6",  
  ],
  
  'rhino': [
    "testsrc/benchmarks/sunspider-0.9.1",
    "testsrc/benchmarks/v8-benchmarks-v5",
    "testsrc/benchmarks/v8-benchmarks-v6",
    "src/org/mozilla/javascript/v8dtoa",
    "toolsrc/org/mozilla/javascript/tools/debugger/treetable",
    "testsrc/org/mozilla/javascript/tests/commonjs",
  ],
  
  'instantbird': [
    # libpurple is LGPL or GPL
    "purple/config",
    "purple/icons",
    "purple/libpurple",
    "purple/libraries",
    "purple/locales",
    
    "other-licenses",
   ],

   'testpilot': [
     "python-modules",
     "extension/content/flot",
   ],

   'mcs': [
     "wordpress/themes/mcs/css",
   ],

  'b2g': [
    "gaia/profile/OfflineCache",
    "gaia/test_apps",
    "prebuilt/ndk",
    "prebuilt/sdk",
    "out",
    "ndk",
    # Don't _think_ we are using this client-side...
    "gecko/other-licenses/bsdiff",

    # Unused bit of libpng
    "external/libpng/contrib",

    # Unused architectures,
    "bionic/libc/arch-sh",
    "bionic/libm/i387",

    # NPOTB
    "gecko/js/src/devtools",
  ],

  'webxray': [
    "vendor",
    "jquery",
    "static-files/codemirror2",
  ],

  'kuma': [
    "vendor",
    "kumascript",
    "media/ckeditor",
    "media/syntaxhighlighter",
    "media/prism",
    "media/ace",
    "media/js/libs",
    "media/fonts",
    "media/gaia/shared",
  ],
} # _g_skip_dirs


# Directories to skip when adding files
_g_skip_add_dirs = {
  '_common': [
  ],
  
  'instantbird': [
    # Lots of small constantly-concatenated files; no header
    "tools/messagestyles/teststyles",
    "instantbird/themes/messages",
  ],
}


# Comment character to use for specific filenames
_g_basename_to_comment = {
    "configure": (["dnl"], ),

    "Makefile": (["#"], ),
    "makefile": (["#"], ),
    "nfspwd": (["#"], ),
    "typemap": (["#"], ),
    "xmplflt.conf": (["#"], ),
    "ldapfriendly": (["#"], ),
    "ldaptemplates.conf": (["#"], ),
    "ldapsearchprefs.conf": (["#"], ),
    "ldapfilter.conf": (["#"], ),
    "README.configure": (["#"], ),
    "Options.txt": (["#"], ),
    "fdsetsize.txt": (["#"], ),
    "prototype": (["#"], ),
    "prototype_i386": (["#"], ),
    "prototype3_i386": (["#"], ),
    "prototype_com": (["#"], ),
    "prototype3_com": (["#"], ),
    "prototype_sparc": (["#"], ),
    "prototype3_sparc": (["#"], ),
    "nglayout.mac": (["#"], ),
    "pkgdepend": (["#"], ),
    "Maketests": (["#"], ),
    "depend": (["#"], ),
    "csh-aliases": (["#"], ),
    "csh-env": (["#"], ),
    ".cshrc": (["#"], ),
    "MANIFEST": (["#"], ),
    "mozconfig": (["#"], ),
    "makecommon": (["#"], ),
    "bld_awk_pkginfo": (["#"], ),
    "prototype_i86pc": (["#"], ),
    "pkgdepend_5_6": (["#"], ),
    "awk_pkginfo-i386": (["#"], ),
    "awk_pkginfo-sparc": (["#"], ),
    "pkgdepend_64bit": (["#"], ),
    "WIN32": (["#"], ),
    "WIN16": (["#"], ),
    "Makefile.linux": (["#"], ),
    "ignored": (["#"], ),

    "README": ([""], ["#"]),
    "copyright": ([""], ),
    "LICENSE": ([""], ["%"]),
    "NOTICE": ([""], ),
    "COPYING": ([""], ),
    "COPYRIGHT": ([""], ),

    "xptcstubs_asm_ppc_darwin.s.m4": (["/*", "*", "*/"], ),
    "xptcstubs_asm_mips.s.m4": (["/*", "*", "*/"], ),

    "nsIDocCharsetTest.txt": (["<!--", "-", "-->"], ),
    "nsIFontListTest.txt": (["<!--", "-", "-->"], ),
    "ComponentListTest.txt": (["<!--", "-", "-->"], ),
    "nsIWebBrowserPersistTest1.txt": (["<!--", "-", "-->"], ),
    "nsIWebBrowserPersistTest2.txt": (["<!--", "-", "-->"], ),
    "nsIWebBrowserPersistTest3.txt": (["<!--", "-", "-->"], ),
    "plugins.txt": (["<!--", "-", "-->"], ),
    "NsISHistoryTestCase1.txt": (["<!--", "-", "-->"], ),
    "EmbedSmokeTest.txt": (["<!--", "-", "-->"], ),

    "lineterm_LICENSE": (["/*", "*", "*/"], ),
    "XMLterm_LICENSE": (["/*", "*", "*/"], ),
    "BrowserView.cpp.mod": (["/*", "*", "*/"], ),
    "header_template": (["/*", "*", "*/"], ),
    "cpp_template": (["/*", "*", "*/"], ),

    "abcFormat470.txt": (["//"], ),
    "opcodes.tbl": (["//"], ),

    "package-manifest":  ([";"], ),
    
    # Instantbird/Chat
    "accounts-aero.css": (["%"], ),
    "blist-aero.css": (["%"], ),
    "conversation-aero.css": (["%"], ),
    "instantbird-aero.css": (["%"], ),
    "tabbrowser-aero.css": (["%"], ),

    "mozconfig-release": (["#"], ),

    "MUTTUCData.txt": (["#"], ),
}


# Comment character (or a set of them) to use for each extension
# When adding new licence blocks, the first will be used
_g_ext_to_comment = {
    ".txt":   (["", ]),
    ".TXT":   (["", ]),
    ".doc":   (["", ]),
    ".build": (["", ]),
    ".1st":   (["", ]),
    ".lsm":   (["", ]),
    ".FP":    (["", ]),
    ".spec":  (["", ]),
    ".android": (["", ]),
    
    ".CPP":    (["/*", "*", "*/"], ["//"]),
    ".cpp":    (["/*", "*", "*/"], ["//"]),
    ".H":      (["/*", "*", "*/"], ["//"]),
    ".h":      (["/*", "*", "*/"], ["//"]),
    ".hxx":    (["/*", "*", "*/"], ["//"]),
    ".c":      (["/*", "*", "*/"], ["//"]),
    ".cc":     (["/*", "*", "*/"], ["//"]),
#    ".css":    (["%"], ["/*", "*", "*/"], ['#']), # *-aero.css files
    ".css":    (["/*", "*", "*/"], ['#']),
    ".js":     (["/*", "*", "*/"], ["//"], ['#']),
    ".idl":    (["/*", "*", "*/"], ),
    ".ut":     (["/*", "*", "*/"], ),
    ".rc":     (["/*", "*", "*/"], ),
    ".rc2":    (["/*", "*", "*/"], ),
    ".RC":     (["/*", "*", "*/"], ),
    ".Prefix": (["/*", "*", "*/"], ),
    ".prefix": (["/*", "*", "*/"], ),
    ".cfg":    (["/*", "*", "*/"], ["#"]),
    ".cp":     (["/*", "*", "*/"], ),
    ".cs":     (["/*", "*", "*/"], ),
    ".java":   (["/*", "*", "*/"], ["//"]),
    ".jst":    (["/*", "*", "*/"], ),
    ".tbl":    (["/*", "*", "*/"], ),
    ".tab":    (["/*", "*", "*/"], ),
    ".msg":    (["/*", "*", "*/"], ),
    ".y":      (["/*", "*", "*/"], ),
    ".r":      (["/*", "*", "*/"], ),
    ".mm":     (["/*", "*", "*/"], ["//"]),
    ".x-ccmap":(["/*", "*", "*/"], ),
    ".ccmap":  (["/*", "*", "*/"], ),
    ".sql":    (["/*", "*", "*/"], ),
    ".pch++":  (["/*", "*", "*/"], ),
    ".xpm":    (["/*", "*", "*/"], ),
    ".uih":    (["/*", "*", "*/"], ),
    ".uil":    (["/*", "*", "*/"], ),
    ".ccmap":  (["/*", "*", "*/"], ),
    ".map":    (["/*", "*", "*/"], ),
    ".win98":  (["/*", "*", "*/"], ),
    ".php":    (["/*", "*", "*/"], ),
    ".php-dist": (["/*", "*", "*/"], ),
    ".module": (["/*", "*", "*/"], ),
    ".m":      (["/*", "*", "*/"], ["//"]),
    ".jnot":   (["/*", "*", "*/"], ),
    ".l":      (["/*", "*", "*/"], ),
    ".htp":    (["/*", "*", "*/"], ),
    ".xs":     (["/*", "*", "*/"], ),
    ".as":     (["/*", "*", "*/"], ),
    ".jsm":    (["/*", "*", "*/"], ),
    ".dep":    (["/*", "*", "*/"], ),
    ".sjs":    (["/*", "*", "*/"], ),
    ".ipdl":   (["/*", "*", "*/"], ),
    ".d":      (["/*", "*", "*/"], ),
    ".strings":(["/*", "*", "*/"], ),
    ".uf":     (["/*", "*", "*/"], ),
    ".dox":    (["/*", "*", "*/"], ),
    ".abs":    (["/*", "*", "*/"], ),
    ".hh":     (["/*", "*", "*/"], ),
    ".pig":    (["/*", "*", "*/"], ),
    ".S":      (["/*", "*", "*/"], ["@"]),
    ".aidl":   (["/*", "*", "*/"], ),
    ".webidl": (["/*", "*", "*/"], ),
    ".java-if":(["/*", "*", "*/"], ),
    ".ipdlh":  (["/*", "*", "*/"], ),
    ".hpp":    (["/*", "*", "*/"], ),

    ".api":    (["/*", "*", "*/"], ['#']),
    ".applescript": (["(*", "*", "*)"], ["--"], ["#"]),

    ".xcconfig": (["//"], ),
    ".st":       (["//"], ),
    ".doctest":  (["//"], ),
    ".jstest":   (["//"], ),
    ".less":     (["//"], ),
    ".proto":    (["//"], ),
    ".pump":     (["//"], ),         
    ".bpf":      (["//"], ),         

# Standard
    ".html": (["<!--", "-", "-->"], ["#"]),
# bedrock/kuma (Jinja)
#    ".html": (["{#", "#", "#}"],),
    ".xml":  (["<!--", "-", "-->"], ["#"]),
    ".xbl":  (["<!--", "-", "-->"], ["#"]),
    ".xsl":  (["<!--", "-", "-->"], ),
    ".xul":  (["<!--", "-", "-->"], ["#"]),
    ".dtd":  (["<!--", "-", "-->"], ["#"]),
    ".rdf":  (["<!--", "-", "-->"], ["#"]),
    ".htm":  (["<!--", "-", "-->"], ),
    ".out":  (["<!--", "-", "-->"], ),
    ".resx": (["<!--", "-", "-->"], ),
    ".bl":   (["<!--", "-", "-->"], ),
    ".xif":  (["<!--", "-", "-->"], ),
    ".xhtml":(["<!--", "-", "-->"], ["#"]),
    ".svg":  (["<!--", "-", "-->"], ),
    ".ttx":  (["<!--", "-", "-->"], ),
    ".atom": (["<!--", "-", "-->"], ),
    ".md":   (["<!--", "-", "-->"], ),
    ".table":(["<!--", "-", "-->"], ),
    ".ejs":  (["<!--", "-", "-->"], ),
    ".jd":   (["<!--", "-", "-->"], ),
    ".man":  (["<!--", "-", "-->"], ['.\"']),
    ".bpr":  (["<!--", "-", "-->"], ['.\"']),
    ".nib":  (["<!--", "-", "-->"], ['.\"']),
    ".xsd":  (["<!--", "-", "-->"], ['.\"']),
    ".user": (["<!--", "-", "-->"], ['.\"']),
    ".sgml": (["<!--", "-", "-->"], ),
    ".ui":   (["<!--", "-", "-->"], ),
    ".vcproj":  (["<!--", "-", "-->"], ),
    ".vcxproj": (["<!--", "-", "-->"], ),
    ".filters": (["<!--", "-", "-->"], ),
    ".plist":   (["<!--", "-", "-->"], ),
    ".graffle": (["<!--", "-", "-->"], ),
    ".xliff":   (["<!--", "-", "-->"], ['.\"']),
    ".cbproj":  (["<!--", "-", "-->"], ['.\"']),
    ".vsprops": (["<!--", "-", "-->"], ['.\"']),

    ".inc":  (["<!--", "-", "-->"], 
              ["#"],
              ["@!"],
              ["/*", "*", "*/"],
              [";"]),

    ".properties": (["#"], ),
    ".win":        (["#"], ),
    ".dsp":        (["#"], ),
    ".exp":        (["#"], ),
    ".mk":         (["#"], ),
    ".mn":         (["#"], ),
    ".mak":        (["#"], ),
    ".MAK":        (["#"], ),
    ".perl":       (["#"], ),
    ".pl":         (["#"], ),
    ".PL":         (["#"], ),
    ".sh":         (["#"], ),
    ".dsw":        (["#"], ),
    ".cgi":        (["#"], ),
    ".pm":         (["#"], ),
    ".pod":        (["#"], ),
    ".src":        (["#"], ),
    ".csh":        (["#"], ),
    ".DLLs":       (["#"], ),
    ".ksh":        (["#"], ),
    ".toc":        (["#"], ),
    ".am":         (["#"], ),
    ".df":         (["#"], ),
    ".client":     (["#"], ),
    ".ref":        (["#"], ), # all of them "Makefile.ref"
    ".ldif":       (["#"], ),
    ".ex":         (["#"], ),
    ".reg":        (["#"], ),
    ".py":         (["#"], [""]),
    ".adb":        (["#"], ),
    ".dtksh":      (["#"], ),
    ".et":         (["#"], ),
    ".stub":       (["#"], ),
    ".nss":        (["#"], ),
    ".os2":        (["#"], ),
    ".Solaris":    (["#"], ),
    ".rep":        (["#"], ),
    ".NSS":        (["#"], ),
    ".server":     (["#"], ),
    ".awk":        (["#"], ),
    ".targ":       (["#"], ),
    ".gnuplot":    (["#"], ),
    ".bash":       (["#"], ),
    ".com":        (["#"], ),
    ".dat":        (["#"], ),
    ".rpm":        (["#"], ),
    ".nsi":        (["#"], ),
    ".nsh":        (["#"], ),
    ".template":   (["#"], ),
    ".ldkd":       (["#"], ),
    ".ldku":       (["#"], ),
    ".arm":        (["#"], ),
    ".qsconf":     (["#"], ),
    ".list":       (["#"], ),
    ".aff":        (["#"], ),
    ".common":     (["#"], ),
    ".manifest":   (["#"], ["<!--", "-", "-->"], ),
    ".excl":       (["#"], ),
    ".yaml":       (["#"], ),
    ".tac":        (["#"], ),
    ".pp":         (["#"], ),
    ".ucm":        (["#"], ),
    ".po":         (["#"], ),
    ".gypi":       (["#"], ),
    ".gyp":        (["#"], ),
    ".prop":       (["#"], ),
    ".appcache":   (["#"], ),
    ".cmake":      (["#"], ),
    ".rsh":        (["#"], ["/*", "*", "*/"]),
    ".kl":         (["#"], ),
    ".msc":        (["#"], ),
    ".kcm":        (["#"], ),
    ".idc":        (["#"], ),
    ".sed":        (["#"], ),
    ".flags":      (["#"], ),

    ".tdf":  ([";"], ),
    ".def":  ([";+#"], [";"]),
    ".DEF":  ([";+#"], [";"]),
    ".ini":  ([";"], ),
    ".it":   ([";"], ),
    ".info": ([";"], ),
    ".nasm": ([";"], ),
    ".lisp": ([";;;"], ),

    ".cmd": (["REM"], ["rem"], ["/*", "*", "*/"]),
    ".bat": (["REM"], ["rem"]),

    ".tex":  (["%"], ),
    ".texi": (["%"], ),

    ".m4":  (["dnl"], ["#"]),
    ".ac":  (["dnl"], ["#"]),

    ".asm": ([";"], ),
    ".vbs": (["'"], ),
    ".il":  (["!"], ),
    ".ad":  (["!"], ),

    ".script": (["(*", " *", "*)"], ),

    ".3x":  (['.\\"'], ),
        
    ".rst": ([".."], ),
    
    # What a mess...
    ".s": (["#"], ["//"], ["/*", "*", "*/"], ["!"], [";"], ["/"], ["@"]),

    # Bugzilla
    ".tmpl":       (["[%#", "#", "#%]"], ["#"], ),
    ".t":          (["#"], ),
    ".conf":       (["#"], ),

    ".license":    (["/*", "*", "*/"], ),
}


# We can find the comment char if the file is extensionless by shebang match
_g_shebang_pattern_to_comment = [
    (re.compile(ur'\A#!.*/bin/(ba)?sh.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*perl.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*php.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*python.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*ruby.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*tclsh.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*wish.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*expect.*$', re.IGNORECASE), (["#"], )),
    (re.compile(ur'\A#!.*env node.*$', re.IGNORECASE), (["/*", "*", "*/"], )),
]
