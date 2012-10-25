{

'Unknown': {
    'regexp': r'^<unknown license>$',
    'title': 'Unknown License',
    'ignore': 1
},

'None Found': {
    'regexp': r'^<none found>$',
    'title': 'None Found',
    'ignore': 1
},

'PD': {
    'regexp': r'^pd$',
    'title': 'Public Domain',
    'ignore': 1
},

'GPL-2.0-with-exception': {
    'regexp': r'^gpl/gpl\w*exception$',
    'title': 'GPL with Exception',
    'ignore': 1
},


'MPL-2.0': {
    # Match tri-license and dual licenses as well; we can use the code under the MPL 2
    # mpl2/mpl2 is files which generate other files
    # mpl2/Capple is the MPL added to a WHAT-WG permissions statement
    'regexp': r'^mpl2|mpl/gpllgpltri|lgpl/mplgpltri|((Credhat|Cmofo|Cmoco)/)*lgpl/mpl|mpl2/mpl2|mpl2/Capple$',
    'title': 'Mozilla Public License 2.0',
},

'DOC-software': {
    'regexp': r'^ace$',
    'title': 'DOC Software License',
},

'BSD-2-Clause-Android': {
    'regexp': r'^Candroid/(2bsd|bsdfileref)$',
    'title': 'Android Open Source License',
},

'BSD-3-Clause-Angle': {
    'regexp': r'^Cangle/(3bsd|bsdfileref)(/Cangle/(3bsd|bsdfileref))?$',
    'title': 'ANGLE License',
},

'Apache-2.0': {
    'regexp': r'^(C\w+/)*apache2$',
    'title': 'Apache License 2.0',
},

'BSD-2-Clause-Apple': {
    'regexp': r'^Capple/2bsd$',
    'title': 'Apple 2-Clause BSD License',
},

'BSD-3-Clause-Apple-Mozilla': {
    'regexp': r'^Capplemozilla/3bsd$',
    'title': 'Apple/Mozilla 3-Clause BSD License',
},

'BSD-2-Clause-Apple-Torch': {
    'regexp': r'^Capple/Ctorch/2bsd$',
    'title': 'Apple/Torch Mobile 2-Clause BSD License',
},

'BSD-3-Clause-Google': {
    'regexp': r'Cgoogle/(3bsd|bsdfileref)(/Cgoogle)?$',
    'title': 'Google 3-Clause BSD License',
},

'BSD-2-Clause-Percival': {
    'regexp': r'^Cpercival/2bsd$',
    'title': 'bspatch License',
},

'HPND-Cairo': {
    # Detecting this copyright holder as a placeholder for all the Cairo
    # licenses
    'regexp': r'^Cworth/hpnd$',
    'title': 'Cairo Component Licenses',
},

'HPND-ISC': {
    'regexp': r'^Cisc/hpnd$',
    'title': 'ISC License',
},

'BSD-3-Clause-Chromium': {
    'regexp': r'^Cchromium/(3bsd|bsdfileref)$',
    'title': 'Chromium License',
},

'HPND-Lucent': {
    'regexp': r'^Clucent/hpnd$',
    'title': 'dtoa License',
},

'BSD-3-Clause-Opentaal': {
    'regexp': r'Copentaal/Cbrouwer/Cdutchtex/3bsd$',
    'title': 'Dutch Spellchecking Dictionary License',
},

'BSD-3-Clause-Eclipse': {
    'regexp': r'^Ceclipse/3bsd$',
    'title': 'Eclipse Distribution License',
},
'MIT-Expat': {
    'regexp': r'^Cthaiopen/(Cexpat/mit|seecopying)$',
    'title': 'Expat License',
},

'BSD-3-Clause-Parakey': {
    'regexp': r'^Cparakey/3bsd$',
    'title': 'Firebug License',
},

'BSD-3-Clause-Apple': {
    'regexp': r'^Capple/3bsd$',
    'title': 'Apple 3-Clause BSD License',
},

'BSD-3-Clause-Google-VP8': {
    'regexp': r'^Cgoogle/3bsd/vp8patent$',
    'title': 'VP8 License',
},

'BSD-3-Clause-Google-iStumbler': {
    'regexp': r'^Cgoogle/3bsd/Cwatt/3bsd$',
    'title': '',
},

'BSD-3-Clause-Pankratov': {
    'regexp': r'^Cpankratov/bsdgeneral2$',
    'title': 'halloc License',
},

'MIT-Harfbuzz': {
    'regexp': r'^(C\w+/)*harfbuzz/mit$',
    'title': 'HarfBuzz License',
},

'MIT-ICU': {
    'regexp': r'^(mpl2/)?icu/mit$',
    'title': 'ICU License',
},

'JPNIC': {
    'regexp': r'^jpnic$',
    'title': 'Japan Network Information Center License',
},

'BSD-2-Clause-jemalloc': {
    'regexp': r'^Cevans/Cmofo/Cfacebook/2bsd$',
    'title': 'jemalloc License',
},

'MIT-jQuery': {
    'regexp': r'^Cresig/mit$',
    'title': 'jQuery License',
},

'HPND-Mozilla': {
    'regexp': r'^Cmofo/hpnd$',
    'title': 'Mozilla HPND License',
},

'BSD-3-Clause-Provos': {
    'regexp': r'^Cprovos/3bsd$',
    'title': 'libevent License',
},

'MIT-libffi': {
    'regexp': r'^Credhatothers/mit$',
    'title': 'libffi License',
},

'BSD-3-Clause-Cisco': {
    'regexp': r'^Ccisco/3bsd$',
    'title': 'libsrtp License',
},

'MIT': {
    'regexp': r'^mit$',
    'title': 'MIT License',
},

'BSD-3-Clause-libyuv': {
    'regexp': r'^Clibyuv/(3bsd|bsdfileref)$',
    'title': 'libyuv License',
},

'BSD-3-Clause-Agejevas': {
    'regexp': r'^Cagejevas/3bsd$',
    'title': 'Lithuanian Spellchecking Dictionary License',
},

'Gemmell': {
    'regexp': r'^gemmell$',
    'title': 'MAAttachedWindow License',
},

'BSD-2-Clause-Chemeris': {
    'regexp': r'^Cchemeris/2bsd$',
    'title': 'MSStdInt License',
},

'BSD-3-Clause-nICEr': {
    'regexp': r'^Cadobe/Cnetworkresonance/3bsd$',
    'title': 'nICEr License',
},

'HPND-OpenVision': {
    'regexp': r'^Copenvision/hpnd$',
    'title': 'OpenVision HPND License',
},

'BSD-3-Clause-NetworkResonance': {
    'regexp': r'^(Cnetworkresonance/)+3bsd$',
    'title': 'nrappkit License',
},

'BSD-4-Clause-RTFM': {
    # We have a waiver for the 4th clause
    'regexp': r'^Crtfm/4bsd$',
    'title': 'Modified ssldump License',
},

'BSD-3-Clause-UCalRegents': {
    'regexp': r'^Cucalregents/3bsd$',
    'title': 'University of California 3-Clause BSD License',
},

'BSD-3-Clause-Miller': {
    'regexp': r'^Ctoddmiller/3bsd$',
    'title': 'Todd C. Miller 3-Clause BSD License',
},

'praton': {
    'regexp': r'^Cucalregents/4bsd/Cdec/hpnd/Cisc/hpnd$',
    'title': 'praton License',
},

'MIT-Mozilla-Maria': {
    'regexp': r'^Cmofo/Cmaria/mit$',
    'title': 'qcms License',
},

'MIT-RedHat': {
    'regexp': r'^Credhat/mit$',
    'title': 'Red Hat MIT License',
},

'BSD-3-Clause-Lebedev': {
    'regexp': r'^Clebedev/3bsd$',
    'title': 'Russian Spellchecking Dictionary License',
},

'BSD-sctp': {
    'regexp': r'^Cpenoff/Ckamal/2bsd(/Ccisco/Cpenoff/3bsd)?$',
    'title': 'SCTP Licenses',
},

'MIT-Matuschak': {
    'regexp': r'^Cmatuschak/mit$',
    'title': 'Sparkle License',
    'comment': "Camino only"
},

'SMSlib': {
    'regexp': r'^Csuitable/mit/3bsd$',
    'title': 'Suitable Systems License',
},

'MIT-SunSoft': {
    'regexp': r'^Csunsoft/mit$',
    'title': 'SunSoft MIT License',
},

'BSD-3-Clause-Cambridge': {
    'regexp': r'^Ccambridge/3bsd$',
    'title': 'University of Cambridge License',
},

'BSD-2-Clause-Szeged': {
    'regexp': r'^Cszeged/2bsd$',
    'title': 'University of Szeged License',
},

'SCOWL': {
    'regexp': r'^Catkinson/hpnd',
    'title': 'US English Spellchecking Dictionary Licenses',
},

'BSD-3-Clause-V8': {
    'regexp': r'^Cv8/3bsd$',
    'title': 'V8 License',
},

'BSD-3-Clause-WebRTC': {
    'regexp': r'^Cwebrtc/(3bsd|bsdfileref)$',
    'title': 'WebRTC License',
},

'BSD-3-Clause-Xiph': {
    'regexp': r'^Cxiph/3bsd$',
    'title': '',
},

'BSD-3-Clause-WebM': {
    'regexp': r'^Cwebm/(3bsd|bsdfileref)$',
    'title': '',
},

'LGPL': {
    'regexp': r'^lgpl$',
    'title': 'GNU Lesser General Public License',
},

'MIT-Mozilla': {
    'regexp': r'^Cmofo/mit$',
    'title': 'Mozilla MIT License',
},

'BSD-3-Clause-IETF-Skype': {
    'regexp': r'^Cietfskype/3bsd$',
    'title': 'libopus License',
},

'BSD-3-Clause-Beazley': {
    'regexp': r'^Cbeazley/3bsd$',
    'title': 'Ply License',
},

'BSD-2-Clause-RichMoore': {
    'regexp': r'^Crichmoore/2bsd$',
    'title': 'CORDIC License',
},

'BSD-2-Clause-Opera': {
    'regexp': r'^Copera/2bsd$',
    'title': 'Opera Software BSD 2-Clause License',
},

'MIT-Khronos': {
    'regexp': r'^(apache/)?Ckhronos/mit$',
    'title': 'Khronos Group MIT License',
},

'MIT-XConsortium': {
    'regexp': r'^Cxconsortium/mit(/pd)?$',
    'title': 'X Consortium MIT License',
},

'MIT-HTML5': {
    'regexp': r'^Csivonen/Cmofo/Capple/mit$',
    'title': 'HTML5 Parser License',
},

# Note: get and ship an updated version of Gentium
'OFL-1.0': {
    # Note: "mit" is a false positive
    'regexp': r'^ofl10/mit$',
    'title': 'Open Font License 1.0',
},

'OFL-1.1': {
    # Note: "mit" is a false positive
    'regexp': r'^ofl11/mit$',
    'title': 'Open Font License 1.1',
},

}


