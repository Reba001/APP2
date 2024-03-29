from __future__ import print_function
import sys
import os
import getopt
import re
import string
import errno
import copy
from jsbeautifier.__version__ import __version__

#
# The MIT License (MIT)

# Copyright (c) 2007-2013 Einar Lielmanis and contributors.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Originally written by Einar Lielmanis et al.,
# Conversion to python by Einar Lielmanis, einar@jsbeautifier.org,
# Parsing improvement for brace-less and semicolon-less statements
#    by Liam Newman <bitwiseman@gmail.com>
# Python is not my native language, feel free to push things around.
#
# Use either from command line (script displays its usage when run
# without any parameters),
#
#
# or, alternatively, use it as a module:
#
#   import jsbeautifier
#   res = jsbeautifier.beautify('your javascript string')
#   res = jsbeautifier.beautify_file('some_file.js')
#
#  you may specify some options:
#
#   opts = jsbeautifier.default_options()
#   opts.indent_size = 2
#   res = jsbeautifier.beautify('some javascript', opts)
#
#
# Here are the available options: (read source)


class BeautifierOptions:
    def __init__(self):
        self.indent_size = 4
        self.indent_char = ' '
        self.indent_with_tabs = False
        self.preserve_newlines = True
        self.max_preserve_newlines = 10
        self.space_in_paren = False
        self.space_in_empty_paren = False
        self.e4x = False
        self.jslint_happy = False
        self.space_after_anon_function = False
        self.brace_style = 'collapse'
        self.keep_array_indentation = False
        self.keep_function_indentation = False
        self.eval_code = False
        self.unescape_strings = False
        self.wrap_line_length = 0
        self.break_chained_methods = False
        self.end_with_newline = False



    def __repr__(self):
        return \
"""indent_size = %d
indent_char = [%s]
preserve_newlines = %s
max_preserve_newlines = %d
space_in_paren = %s
jslint_happy = %s
space_after_anon_function = %s
indent_with_tabs = %s
brace_style = %s
keep_array_indentation = %s
eval_code = %s
wrap_line_length = %s
unescape_strings = %s
""" % ( self.indent_size,
        self.indent_char,
        self.preserve_newlines,
        self.max_preserve_newlines,
        self.space_in_paren,
        self.jslint_happy,
        self.space_after_anon_function,
        self.indent_with_tabs,
        self.brace_style,
        self.keep_array_indentation,
        self.eval_code,
        self.wrap_line_length,
        self.unescape_strings,
        )


class BeautifierFlags:
    def __init__(self, mode):
        self.mode = mode
        self.parent = None
        self.last_text = ''
        self.last_word = ''
        self.declaration_statement = False
        self.declaration_assignment = False
        self.multiline_frame = False
        self.if_block = False
        self.else_block = False
        self.do_block = False
        self.do_while = False
        self.in_case = False
        self.in_case_statement = False
        self.case_body = False
        self.indentation_level = 0
        self.line_indent_level = 0
        self.start_line_index = 0
        self.ternary_depth = 0

    def apply_base(self, flags_base, added_newline):
        next_indent_level = flags_base.indentation_level
        if not added_newline and \
            flags_base.line_indent_level > next_indent_level:
            next_indent_level = flags_base.line_indent_level

        self.parent = flags_base
        self.last_text = flags_base.last_text
        self.last_word = flags_base.last_word
        self.indentation_level = next_indent_level

class Acorn:
    def __init__(self):
        # This is not pretty, but given how we did the version import
        # it is the only way to do this without having setup.py fail on a missing six dependency.
        self.six = __import__("six")
        # This section of code was translated to python from acorn (javascript).
        #
        # Acorn was written by Marijn Haverbeke and released under an MIT
        # license. The Unicode regexps (for identifiers and whitespace) were
        # taken from [Esprima](http://esprima.org) by Ariya Hidayat.
        #
        # Git repositories for Acorn are available at
        #
        #     http://marijnhaverbeke.nl/git/acorn
        #     https://github.com/marijnh/acorn.git

        # ## Character categories

        # Big ugly regular expressions that match characters in the
        # whitespace, identifier, and identifier-start categories. These
        # are only applied when a character is found to actually have a
        # code point above 128.

        self.nonASCIIwhitespace = re.compile(self.six.u("[\u1680\u180e\u2000-\u200a\u202f\u205f\u3000\ufeff]"))
        self.nonASCIIidentifierStartChars = self.six.u("\xaa\xb5\xba\xc0-\xd6\xd8-\xf6\xf8-\u02c1\u02c6-\u02d1\u02e0-\u02e4\u02ec\u02ee\u0370-\u0374\u0376\u0377\u037a-\u037d\u0386\u0388-\u038a\u038c\u038e-\u03a1\u03a3-\u03f5\u03f7-\u0481\u048a-\u0527\u0531-\u0556\u0559\u0561-\u0587\u05d0-\u05ea\u05f0-\u05f2\u0620-\u064a\u066e\u066f\u0671-\u06d3\u06d5\u06e5\u06e6\u06ee\u06ef\u06fa-\u06fc\u06ff\u0710\u0712-\u072f\u074d-\u07a5\u07b1\u07ca-\u07ea\u07f4\u07f5\u07fa\u0800-\u0815\u081a\u0824\u0828\u0840-\u0858\u08a0\u08a2-\u08ac\u0904-\u0939\u093d\u0950\u0958-\u0961\u0971-\u0977\u0979-\u097f\u0985-\u098c\u098f\u0990\u0993-\u09a8\u09aa-\u09b0\u09b2\u09b6-\u09b9\u09bd\u09ce\u09dc\u09dd\u09df-\u09e1\u09f0\u09f1\u0a05-\u0a0a\u0a0f\u0a10\u0a13-\u0a28\u0a2a-\u0a30\u0a32\u0a33\u0a35\u0a36\u0a38\u0a39\u0a59-\u0a5c\u0a5e\u0a72-\u0a74\u0a85-\u0a8d\u0a8f-\u0a91\u0a93-\u0aa8\u0aaa-\u0ab0\u0ab2\u0ab3\u0ab5-\u0ab9\u0abd\u0ad0\u0ae0\u0ae1\u0b05-\u0b0c\u0b0f\u0b10\u0b13-\u0b28\u0b2a-\u0b30\u0b32\u0b33\u0b35-\u0b39\u0b3d\u0b5c\u0b5d\u0b5f-\u0b61\u0b71\u0b83\u0b85-\u0b8a\u0b8e-\u0b90\u0b92-\u0b95\u0b99\u0b9a\u0b9c\u0b9e\u0b9f\u0ba3\u0ba4\u0ba8-\u0baa\u0bae-\u0bb9\u0bd0\u0c05-\u0c0c\u0c0e-\u0c10\u0c12-\u0c28\u0c2a-\u0c33\u0c35-\u0c39\u0c3d\u0c58\u0c59\u0c60\u0c61\u0c85-\u0c8c\u0c8e-\u0c90\u0c92-\u0ca8\u0caa-\u0cb3\u0cb5-\u0cb9\u0cbd\u0cde\u0ce0\u0ce1\u0cf1\u0cf2\u0d05-\u0d0c\u0d0e-\u0d10\u0d12-\u0d3a\u0d3d\u0d4e\u0d60\u0d61\u0d7a-\u0d7f\u0d85-\u0d96\u0d9a-\u0db1\u0db3-\u0dbb\u0dbd\u0dc0-\u0dc6\u0e01-\u0e30\u0e32\u0e33\u0e40-\u0e46\u0e81\u0e82\u0e84\u0e87\u0e88\u0e8a\u0e8d\u0e94-\u0e97\u0e99-\u0e9f\u0ea1-\u0ea3\u0ea5\u0ea7\u0eaa\u0eab\u0ead-\u0eb0\u0eb2\u0eb3\u0ebd\u0ec0-\u0ec4\u0ec6\u0edc-\u0edf\u0f00\u0f40-\u0f47\u0f49-\u0f6c\u0f88-\u0f8c\u1000-\u102a\u103f\u1050-\u1055\u105a-\u105d\u1061\u1065\u1066\u106e-\u1070\u1075-\u1081\u108e\u10a0-\u10c5\u10c7\u10cd\u10d0-\u10fa\u10fc-\u1248\u124a-\u124d\u1250-\u1256\u1258\u125a-\u125d\u1260-\u1288\u128a-\u128d\u1290-\u12b0\u12b2-\u12b5\u12b8-\u12be\u12c0\u12c2-\u12c5\u12c8-\u12d6\u12d8-\u1310\u1312-\u1315\u1318-\u135a\u1380-\u138f\u13a0-\u13f4\u1401-\u166c\u166f-\u167f\u1681-\u169a\u16a0-\u16ea\u16ee-\u16f0\u1700-\u170c\u170e-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176c\u176e-\u1770\u1780-\u17b3\u17d7\u17dc\u1820-\u1877\u1880-\u18a8\u18aa\u18b0-\u18f5\u1900-\u191c\u1950-\u196d\u1970-\u1974\u1980-\u19ab\u19c1-\u19c7\u1a00-\u1a16\u1a20-\u1a54\u1aa7\u1b05-\u1b33\u1b45-\u1b4b\u1b83-\u1ba0\u1bae\u1baf\u1bba-\u1be5\u1c00-\u1c23\u1c4d-\u1c4f\u1c5a-\u1c7d\u1ce9-\u1cec\u1cee-\u1cf1\u1cf5\u1cf6\u1d00-\u1dbf\u1e00-\u1f15\u1f18-\u1f1d\u1f20-\u1f45\u1f48-\u1f4d\u1f50-\u1f57\u1f59\u1f5b\u1f5d\u1f5f-\u1f7d\u1f80-\u1fb4\u1fb6-\u1fbc\u1fbe\u1fc2-\u1fc4\u1fc6-\u1fcc\u1fd0-\u1fd3\u1fd6-\u1fdb\u1fe0-\u1fec\u1ff2-\u1ff4\u1ff6-\u1ffc\u2071\u207f\u2090-\u209c\u2102\u2107\u210a-\u2113\u2115\u2119-\u211d\u2124\u2126\u2128\u212a-\u212d\u212f-\u2139\u213c-\u213f\u2145-\u2149\u214e\u2160-\u2188\u2c00-\u2c2e\u2c30-\u2c5e\u2c60-\u2ce4\u2ceb-\u2cee\u2cf2\u2cf3\u2d00-\u2d25\u2d27\u2d2d\u2d30-\u2d67\u2d6f\u2d80-\u2d96\u2da0-\u2da6\u2da8-\u2dae\u2db0-\u2db6\u2db8-\u2dbe\u2dc0-\u2dc6\u2dc8-\u2dce\u2dd0-\u2dd6\u2dd8-\u2dde\u2e2f\u3005-\u3007\u3021-\u3029\u3031-\u3035\u3038-\u303c\u3041-\u3096\u309d-\u309f\u30a1-\u30fa\u30fc-\u30ff\u3105-\u312d\u3131-\u318e\u31a0-\u31ba\u31f0-\u31ff\u3400-\u4db5\u4e00-\u9fcc\ua000-\ua48c\ua4d0-\ua4fd\ua500-\ua60c\ua610-\ua61f\ua62a\ua62b\ua640-\ua66e\ua67f-\ua697\ua6a0-\ua6ef\ua717-\ua71f\ua722-\ua788\ua78b-\ua78e\ua790-\ua793\ua7a0-\ua7aa\ua7f8-\ua801\ua803-\ua805\ua807-\ua80a\ua80c-\ua822\ua840-\ua873\ua882-\ua8b3\ua8f2-\ua8f7\ua8fb\ua90a-\ua925\ua930-\ua946\ua960-\ua97c\ua984-\ua9b2\ua9cf\uaa00-\uaa28\uaa40-\uaa42\uaa44-\uaa4b\uaa60-\uaa76\uaa7a\uaa80-\uaaaf\uaab1\uaab5\uaab6\uaab9-\uaabd\uaac0\uaac2\uaadb-\uaadd\uaae0-\uaaea\uaaf2-\uaaf4\uab01-\uab06\uab09-\uab0e\uab11-\uab16\uab20-\uab26\uab28-\uab2e\uabc0-\uabe2\uac00-\ud7a3\ud7b0-\ud7c6\ud7cb-\ud7fb\uf900-\ufa6d\ufa70-\ufad9\ufb00-\ufb06\ufb13-\ufb17\ufb1d\ufb1f-\ufb28\ufb2a-\ufb36\ufb38-\ufb3c\ufb3e\ufb40\ufb41\ufb43\ufb44\ufb46-\ufbb1\ufbd3-\ufd3d\ufd50-\ufd8f\ufd92-\ufdc7\ufdf0-\ufdfb\ufe70-\ufe74\ufe76-\ufefc\uff21-\uff3a\uff41-\uff5a\uff66-\uffbe\uffc2-\uffc7\uffca-\uffcf\uffd2-\uffd7\uffda-\uffdc")
        self.nonASCIIidentifierChars = self.six.u("\u0300-\u036f\u0483-\u0487\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7\u0610-\u061a\u0620-\u0649\u0672-\u06d3\u06e7-\u06e8\u06fb-\u06fc\u0730-\u074a\u0800-\u0814\u081b-\u0823\u0825-\u0827\u0829-\u082d\u0840-\u0857\u08e4-\u08fe\u0900-\u0903\u093a-\u093c\u093e-\u094f\u0951-\u0957\u0962-\u0963\u0966-\u096f\u0981-\u0983\u09bc\u09be-\u09c4\u09c7\u09c8\u09d7\u09df-\u09e0\u0a01-\u0a03\u0a3c\u0a3e-\u0a42\u0a47\u0a48\u0a4b-\u0a4d\u0a51\u0a66-\u0a71\u0a75\u0a81-\u0a83\u0abc\u0abe-\u0ac5\u0ac7-\u0ac9\u0acb-\u0acd\u0ae2-\u0ae3\u0ae6-\u0aef\u0b01-\u0b03\u0b3c\u0b3e-\u0b44\u0b47\u0b48\u0b4b-\u0b4d\u0b56\u0b57\u0b5f-\u0b60\u0b66-\u0b6f\u0b82\u0bbe-\u0bc2\u0bc6-\u0bc8\u0bca-\u0bcd\u0bd7\u0be6-\u0bef\u0c01-\u0c03\u0c46-\u0c48\u0c4a-\u0c4d\u0c55\u0c56\u0c62-\u0c63\u0c66-\u0c6f\u0c82\u0c83\u0cbc\u0cbe-\u0cc4\u0cc6-\u0cc8\u0cca-\u0ccd\u0cd5\u0cd6\u0ce2-\u0ce3\u0ce6-\u0cef\u0d02\u0d03\u0d46-\u0d48\u0d57\u0d62-\u0d63\u0d66-\u0d6f\u0d82\u0d83\u0dca\u0dcf-\u0dd4\u0dd6\u0dd8-\u0ddf\u0df2\u0df3\u0e34-\u0e3a\u0e40-\u0e45\u0e50-\u0e59\u0eb4-\u0eb9\u0ec8-\u0ecd\u0ed0-\u0ed9\u0f18\u0f19\u0f20-\u0f29\u0f35\u0f37\u0f39\u0f41-\u0f47\u0f71-\u0f84\u0f86-\u0f87\u0f8d-\u0f97\u0f99-\u0fbc\u0fc6\u1000-\u1029\u1040-\u1049\u1067-\u106d\u1071-\u1074\u1082-\u108d\u108f-\u109d\u135d-\u135f\u170e-\u1710\u1720-\u1730\u1740-\u1750\u1772\u1773\u1780-\u17b2\u17dd\u17e0-\u17e9\u180b-\u180d\u1810-\u1819\u1920-\u192b\u1930-\u193b\u1951-\u196d\u19b0-\u19c0\u19c8-\u19c9\u19d0-\u19d9\u1a00-\u1a15\u1a20-\u1a53\u1a60-\u1a7c\u1a7f-\u1a89\u1a90-\u1a99\u1b46-\u1b4b\u1b50-\u1b59\u1b6b-\u1b73\u1bb0-\u1bb9\u1be6-\u1bf3\u1c00-\u1c22\u1c40-\u1c49\u1c5b-\u1c7d\u1cd0-\u1cd2\u1d00-\u1dbe\u1e01-\u1f15\u200c\u200d\u203f\u2040\u2054\u20d0-\u20dc\u20e1\u20e5-\u20f0\u2d81-\u2d96\u2de0-\u2dff\u3021-\u3028\u3099\u309a\ua640-\ua66d\ua674-\ua67d\ua69f\ua6f0-\ua6f1\ua7f8-\ua800\ua806\ua80b\ua823-\ua827\ua880-\ua881\ua8b4-\ua8c4\ua8d0-\ua8d9\ua8f3-\ua8f7\ua900-\ua909\ua926-\ua92d\ua930-\ua945\ua980-\ua983\ua9b3-\ua9c0\uaa00-\uaa27\uaa40-\uaa41\uaa4c-\uaa4d\uaa50-\uaa59\uaa7b\uaae0-\uaae9\uaaf2-\uaaf3\uabc0-\uabe1\uabec\uabed\uabf0-\uabf9\ufb20-\ufb28\ufe00-\ufe0f\ufe20-\ufe26\ufe33\ufe34\ufe4d-\ufe4f\uff10-\uff19\uff3f")
        self.nonASCIIidentifierStart = re.compile("[" + self.nonASCIIidentifierStartChars + "]")
        self.nonASCIIidentifier = re.compile("[" + self.nonASCIIidentifierStartChars + self.nonASCIIidentifierChars + "]")

        # Whether a single character denotes a newline.

        self.newline = re.compile(self.six.u("[\n\r\u2028\u2029]"))

        # Matches a whole line break (where CRLF is considered a single
        # line break). Used to count lines.

        self.lineBreak = re.compile(self.six.u("\r\n|[\n\r\u2028\u2029]"))


    # Test whether a given character code starts an identifier.
    def isIdentifierStart(self, code):
        if code < 65:
            return code == 36
        if code < 91:
            return True
        if code < 97:
            return code == 95
        if code < 123:
            return True
        return code >= 0xaa and self.nonASCIIidentifierStart.match(self.six.unichr(code)) != None

    # Test whether a given character is part of an identifier.
    def isIdentifierChar(self, code):
        if code < 48:
            return code == 36
        if code < 58:
            return True
        if code < 65:
            return False
        if code < 91:
            return True
        if code < 97:
            return code == 95
        if code < 123:
            return True
        return code >= 0xaa and self.nonASCIIidentifier.match(self.six.unichr(code)) != None

class Token:
    def __init__(self, type, text, newlines = 0, whitespace_before = [], mode = None, parent = None):
        self.type = type
        self.text = text
        self.comments_before = []
        self.newlines = newlines
        self.wanted_newline = newlines > 0
        self.whitespace_before = whitespace_before
        self.parent = None


def default_options():
    return BeautifierOptions()


def beautify(string, opts = default_options() ):
    b = Beautifier()
    return b.beautify(string, opts)

def beautify_file(file_name, opts = default_options() ):
    if file_name == '-': # stdin
        stream = sys.stdin
    else:
        stream = open(file_name)

    return beautify(''.join(stream.readlines()), opts)


def usage(stream=sys.stdout):

    print("jsbeautifier.py@" + __version__ + """

Javascript beautifier (http://jsbeautifier.org/)

Usage: jsbeautifier.py [options] <infile>

    <infile> can be "-", which means stdin.
    <outfile> defaults to stdout

Input options:

 -i,  --stdin                      read input from stdin

Output options:

 -s,  --indent-size=NUMBER         indentation size. (default 4).
 -c,  --indent-char=CHAR           character to indent with. (default space).
 -t,  --indent-with-tabs           Indent with tabs, overrides -s and -c
 -d,  --disable-preserve-newlines  do not preserve existing line breaks.
 -P,  --space-in-paren             add padding spaces within paren, ie. f( a, b )
 -E,  --space-in-empty-paren       Add a single space inside empty paren, ie. f( )
 -j,  --jslint-happy               more jslint-compatible output
 -a,  --space_after_anon_function  add a space before an anonymous function's parens, ie. function ()
 -b,  --brace-style=collapse       brace style (collapse, expand, end-expand)
 -k,  --keep-array-indentation     keep array indentation.
 -o,  --outfile=FILE               specify a file to output to (default stdout)
 -f,  --keep-function-indentation  Do not re-indent function bodies defined in var lines.
 -x,  --unescape-strings           Decode printable chars encoded in \\xNN notation.
 -X,  --e4x                        Pass E4X xml literals through untouched
 -w,  --wrap-line-length                   Attempt to wrap line when it exceeds this length.
                                   NOTE: Line continues until next wrap point is found.
 -n, --end_with_newline            End output with newline

Rarely needed options:

 --eval-code                       evaluate code if a JS interpreter is
                                   installed. May be useful with some obfuscated
                                   script but poses a potential security issue.

 -l,  --indent-level=NUMBER        initial indentation level. (default 0).

 -h,  --help, --usage              prints this help statement.
 -v, --version                     Show the version

""", file=stream)
    if stream == sys.stderr:
        return 1
    else:
        return 0



class MODE:
      BlockStatement, Statement, ObjectLiteral, ArrayLiteral, \
      ForInitializer, Conditional, Expression = range(7)

class Beautifier:

    def __init__(self, opts = default_options() ):

        self.opts = copy.copy(opts)
        self.blank_state()

    def blank_state(self, js_source_text = None):

        # internal flags
        self.flags = None
        self.previous_flags = None
        self.flag_store = []
        self.tokens = []
        self.token_pos = 0


        # force opts.space_after_anon_function to true if opts.jslint_happy
        if self.opts.jslint_happy:
            self.opts.space_after_anon_function = True

        if self.opts.indent_with_tabs:
            self.opts.indent_char = "\t"
            self.opts.indent_size = 1

        self.indent_string = self.opts.indent_char * self.opts.indent_size

        self.baseIndentString = ''
        self.last_type = 'TK_START_BLOCK' # last token type
        self.last_last_text = ''         # pre-last token text

        preindent_index = 0;
        if not js_source_text == None and len(js_source_text) > 0:
            while preindent_index < len(js_source_text) and \
                    js_source_text[preindent_index] in [' ', '\t'] :
                self.baseIndentString += js_source_text[preindent_index]
                preindent_index += 1
            js_source_text = js_source_text[preindent_index:]

        self.output = Output(self.indent_string, self.baseIndentString)

        self.set_mode(MODE.BlockStatement)
        return js_source_text

    def beautify(self, s, opts = None ):

        if opts != None:
            self.opts = copy.copy(opts)

        if self.opts.brace_style not in ['expand', 'collapse', 'end-expand']:
            raise(Exception('opts.brace_style must be "expand", "collapse" or "end-expand".'))

        s = self.blank_state(s)

        input = self.unpack(s, self.opts.eval_code)

        self.handlers = {
            'TK_START_EXPR': self.handle_start_expr,
            'TK_END_EXPR': self.handle_end_expr,
            'TK_START_BLOCK': self.handle_start_block,
            'TK_END_BLOCK': self.handle_end_block,
            'TK_WORD': self.handle_word,
            'TK_RESERVED': self.handle_word,
            'TK_SEMICOLON': self.handle_semicolon,
            'TK_STRING': self.handle_string,
            'TK_EQUALS': self.handle_equals,
            'TK_OPERATOR': self.handle_operator,
            'TK_COMMA': self.handle_comma,
            'TK_BLOCK_COMMENT': self.handle_block_comment,
            'TK_INLINE_COMMENT': self.handle_inline_comment,
            'TK_COMMENT': self.handle_comment,
            'TK_DOT': self.handle_dot,
            'TK_UNKNOWN': self.handle_unknown,
            'TK_EOF': self.handle_eof
        }

        self.tokens = Tokenizer(input, self.opts, self.indent_string).tokenize()
        self.token_pos = 0

        while not self.get_token() == None:
            local_token = self.get_token()

            for comment_token in local_token.comments_before:
                # The cleanest handling of inline comments is to treat them as though they aren't there.
                # Just continue formatting and the behavior should be logical.
                # Also ignore unknown tokens.  Again, this should result in better behavior.
                    self.handle_token(comment_token)

            self.handle_token(local_token)

            self.last_last_text = self.flags.last_text
            self.last_type = local_token.type
            self.flags.last_text = local_token.text
            self.token_pos += 1


        sweet_code = self.output.get_code()
        if self.opts.end_with_newline:
            sweet_code += "\n"

        return sweet_code

    def handle_token(self, local_token):
        newlines = local_token.newlines
        keep_whitespace = self.opts.keep_array_indentation and self.is_array(self.flags.mode)

        if keep_whitespace:
             for i in range(newlines):
                    self.print_newline(i > 0)
        else: # not keep_whitespace
            if self.opts.max_preserve_newlines != 0 and newlines > self.opts.max_preserve_newlines:
                newlines = self.opts.max_preserve_newlines

            if self.opts.preserve_newlines and newlines > 1:
                self.print_newline()
                for i in range(1, newlines):
                    self.print_newline(True)

        self.handlers[local_token.type](local_token)


    def unpack(self, source, evalcode=False):
        import jsbeautifier.unpackers as unpackers
        try:
            return unpackers.run(source, evalcode)
        except unpackers.UnpackingError as error:
            print('error:', error)
            return ''

    def is_special_word(self, s):
        return s in ['case', 'return', 'do', 'if', 'throw', 'else']

    def is_array(self, mode):
        return mode == MODE.ArrayLiteral


    def is_expression(self, mode):
        return mode in [MODE.Expression, MODE.ForInitializer, MODE.Conditional]


    def allow_wrap_or_preserved_newline(self, current_token, force_linewrap = False):
        if self.output.just_added_newline():
            return

        if (self.opts.preserve_newlines and current_token.wanted_newline) or force_linewrap:
            self.print_newline(preserve_statement_flags = True)
        elif self.opts.wrap_line_length > 0 and self.output.current_line.get_item_count() > 0:
            # never wrap the first token of a line.
            proposed_line_length = self.output.current_line.get_character_count() + len(current_token.text)
            if self.output.space_before_token:
                proposed_line_length += 1

            if proposed_line_length >= self.opts.wrap_line_length:
                self.print_newline(preserve_statement_flags = True)


    def print_newline(self, force_newline = False, preserve_statement_flags = False):
        if not preserve_statement_flags:
            if self.flags.last_text != ';' and self.flags.last_text != ',' and self.flags.last_text != '=' and self.last_type != 'TK_OPERATOR':
                while self.flags.mode == MODE.Statement and not self.flags.if_block and not self.flags.do_block:
                    self.restore_mode()

        if self.output.add_new_line(force_newline):
            self.flags.multiline_frame = True

    def print_token_line_indentation(self, current_token):
        if self.output.just_added_newline():
            line = self.output.current_line
            if self.opts.keep_array_indentation and self.is_array(self.flags.mode) and current_token.wanted_newline:
                # prevent removing of this whitespace as redundant
                line.push('')
                for item in current_token.whitespace_before:
                    line.push(item)

            elif self.output.add_indent_string(self.flags.indentation_level):
                self.flags.line_indent_level = self.flags.indentation_level


    def print_token(self, current_token, s=None):
        if s == None:
            s = current_token.text

        self.print_token_line_indentation(current_token)
        self.output.add_token(s);


    def indent(self):
        self.flags.indentation_level += 1

    def deindent(self):
        allow_deindent = self.flags.indentation_level > 0 and ((self.flags.parent == None) or self.flags.indentation_level > self.flags.parent.indentation_level)

        if allow_deindent:
            self.flags.indentation_level -= 1

    def set_mode(self, mode):
        if self.flags:
            self.flag_store.append(self.flags)
            self.previous_flags = self.flags
        else:
            self.previous_flags = BeautifierFlags(mode)

        self.flags = BeautifierFlags(mode)
        self.flags.apply_base(self.previous_flags, self.output.just_added_newline())
        self.flags.start_line_index = self.output.get_line_number();

    def restore_mode(self):
        if len(self.flag_store) > 0:
            self.previous_flags = self.flags
            self.flags = self.flag_store.pop()
            if self.previous_flags.mode == MODE.Statement:
                self.output.remove_redundant_indentation(self.previous_flags)


    def start_of_object_property(self):
        return self.flags.parent.mode == MODE.ObjectLiteral and self.flags.mode == MODE.Statement and \
                ((self.flags.last_text == ':' and self.flags.ternary_depth == 0) or (self.last_type == 'TK_RESERVED' and self.flags.last_text in ['get', 'set']))

    def start_of_statement(self, current_token):
        if (
            (self.last_type == 'TK_RESERVED' and self.flags.last_text in ['var', 'let', 'const'] and current_token.type == 'TK_WORD') \
                or (self.last_type == 'TK_RESERVED' and self.flags.last_text== 'do') \
                or (self.last_type == 'TK_RESERVED' and self.flags.last_text== 'return' and not current_token.wanted_newline) \
                or (self.last_type == 'TK_RESERVED' and self.flags.last_text == 'else' and not (current_token.type == 'TK_RESERVED' and current_token.text == 'if' )) \
                or (self.last_type == 'TK_END_EXPR' and (self.previous_flags.mode == MODE.ForInitializer or self.previous_flags.mode == MODE.Conditional)) \
                or (self.last_type == 'TK_WORD' and self.flags.mode == MODE.BlockStatement \
                    and not self.flags.in_case
                    and not (current_token.text == '--' or current_token.text == '++')
                    and current_token.type != 'TK_WORD' and current_token.type != 'TK_RESERVED') \
                or (self.flags.mode == MODE.ObjectLiteral and \
                    ((self.flags.last_text == ':' and self.flags.ternary_depth == 0) or (self.last_type == 'TK_RESERVED' and self.flags.last_text in ['get', 'set'])))
                ):

            self.set_mode(MODE.Statement)
            self.indent()

            if self.last_type == 'TK_RESERVED' and self.flags.last_text in ['var', 'let', 'const'] and current_token.type == 'TK_WORD':
                self.flags.declaration_statement = True

            # Issue #276:
            # If starting a new statement with [if, for, while, do], push to a new line.
            # if (a) if (b) if(c) d(); else e(); else f();
            if not self.start_of_object_property():
                self.allow_wrap_or_preserved_newline(current_token, current_token.type == 'TK_RESERVED' and current_token.text in ['do', 'for', 'if', 'while'])

            return True
        else:
            return False

    def get_token(self, offset = 0):
        index = self.token_pos + offset
        if index < 0 or index >= len(self.tokens):
            return None
        else:
            return self.tokens[index]


    def handle_start_expr(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            pass

        next_mode = MODE.Expression

        if current_token.text == '[':
            if self.last_type == 'TK_WORD' or self.flags.last_text == ')':
                if self.last_type == 'TK_RESERVED' and self.flags.last_text in Tokenizer.line_starters:
                    self.output.space_before_token = True
                self.set_mode(next_mode)
                self.print_token(current_token)
                self.indent()
                if self.opts.space_in_paren:
                    self.output.space_before_token = True
                return

            next_mode = MODE.ArrayLiteral

            if self.is_array(self.flags.mode):
                if self.flags.last_text == '[' or (
                    self.flags.last_text == ',' and (self.last_last_text == ']' or self.last_last_text == '}')):
                    # ], [ goes to a new line
                    # }, [ goes to a new line
                    if not self.opts.keep_array_indentation:
                        self.print_newline()

        else:
            if self.last_type == 'TK_RESERVED' and self.flags.last_text == 'for':
                next_mode = MODE.ForInitializer
            elif self.last_type == 'TK_RESERVED' and self.flags.last_text in ['if', 'while']:
                next_mode = MODE.Conditional
            else:
                next_mode = MODE.Expression


        if self.flags.last_text == ';' or self.last_type == 'TK_START_BLOCK':
            self.print_newline()
        elif self.last_type in ['TK_END_EXPR', 'TK_START_EXPR', 'TK_END_BLOCK'] or self.flags.last_text == '.':
            # do nothing on (( and )( and ][ and ]( and .(
            # TODO: Consider whether forcing this is required.  Review failing tests when removed.
            self.allow_wrap_or_preserved_newline(current_token, current_token.wanted_newline)

        elif not (self.last_type == 'TK_RESERVED' and current_token.text == '(') and self.last_type not in ['TK_WORD', 'TK_OPERATOR']:
            self.output.space_before_token = True
        elif (self.last_type == 'TK_RESERVED' and (self.flags.last_word == 'function' or self.flags.last_word == 'typeof')) or \
            (self.flags.last_text == '*' and self.last_last_text =='function'):
            # function() vs function (), typeof() vs typeof ()
            if self.opts.space_after_anon_function:
                self.output.space_before_token = True
        elif self.last_type == 'TK_RESERVED' and (self.flags.last_text in Tokenizer.line_starters or self.flags.last_text == 'catch'):
            # TODO: option space_before_conditional
            self.output.space_before_token = True

        # Support of this kind of newline preservation:
        # a = (b &&
        #     (c || d));
        if self.last_type in ['TK_EQUALS', 'TK_OPERATOR']:
            if not self.start_of_object_property():
                self.allow_wrap_or_preserved_newline(current_token)

        self.set_mode(next_mode)
        self.print_token(current_token)

        if self.opts.space_in_paren:
            self.output.space_before_token = True

        # In all cases, if we newline while inside an expression it should be indented.
        self.indent()



    def handle_end_expr(self, current_token):
        # statements inside expressions are not valid syntax, but...
        # statements must all be closed when their container closes
        while self.flags.mode == MODE.Statement:
            self.restore_mode()

        if self.flags.multiline_frame:
            self.allow_wrap_or_preserved_newline(current_token, current_token.text == ']' and self.is_array(self.flags.mode) and not self.opts.keep_array_indentation)

        if self.opts.space_in_paren:
            if self.last_type == 'TK_START_EXPR' and not self.opts.space_in_empty_paren:
                # empty parens are always "()" and "[]", not "( )" or "[ ]"
                self.output.space_before_token = False
                self.output.trim()
            else:
                self.output.space_before_token = True

        if current_token.text == ']' and self.opts.keep_array_indentation:
            self.print_token(current_token)
            self.restore_mode()
        else:
            self.restore_mode()
            self.print_token(current_token)

        self.output.remove_redundant_indentation(self.previous_flags)

        # do {} while () // no statement required after
        if self.flags.do_while and self.previous_flags.mode == MODE.Conditional:
            self.previous_flags.mode = MODE.Expression
            self.flags.do_block = False
            self.flags.do_while = False

    def handle_start_block(self, current_token):
        # Check if this is a BlockStatement that should be treated as a ObjectLiteral
        next_token = self.get_token(1)
        second_token = self.get_token(2)
        if second_token != None and \
            ((second_token.text == ':' and next_token.type in ['TK_STRING', 'TK_WORD', 'TK_RESERVED']) \
                or (next_token.text in ['get', 'set'] and second_token.type in ['TK_WORD', 'TK_RESERVED'])):
            # We don't support TypeScript,but we didn't break it for a very long time.
            # We'll try to keep not breaking it.
            if not self.last_last_text in ['class','interface']:
                self.set_mode(MODE.ObjectLiteral);
            else:
                self.set_mode(MODE.BlockStatement)
        else:
            self.set_mode(MODE.BlockStatement)

        empty_braces = (not next_token == None) and len(next_token.comments_before) == 0 and next_token.text == '}'
        empty_anonymous_function = empty_braces and self.flags.last_word == 'function' and \
            self.last_type == 'TK_END_EXPR'

        if self.opts.brace_style == 'expand':
            if self.last_type != 'TK_OPERATOR' and \
                (empty_anonymous_function or
                    self.last_type == 'TK_EQUALS' or
                    (self.last_type == 'TK_RESERVED' and self.is_special_word(self.flags.last_text) and self.flags.last_text != 'else')):
                self.output.space_before_token = True
            else:
                self.print_newline(preserve_statement_flags = True)
        else: # collapse
            if self.last_type not in ['TK_OPERATOR', 'TK_START_EXPR']:
                if self.last_type == 'TK_START_BLOCK':
                    self.print_newline()
                else:
                    self.output.space_before_token = True
            else:
                # if TK_OPERATOR or TK_START_EXPR
                if self.is_array(self.previous_flags.mode) and self.flags.last_text == ',':
                    if self.last_last_text == '}':
                        self.output.space_before_token = True
                    else:
                        self.print_newline()

        self.print_token(current_token)
        self.indent()


    def handle_end_block(self, current_token):
        # statements must all be closed when their container closes
        while self.flags.mode == MODE.Statement:
            self.restore_mode()

        empty_braces = self.last_type == 'TK_START_BLOCK'
        if self.opts.brace_style == 'expand':
            if not empty_braces:
                self.print_newline()
        else:
            # skip {}
            if not empty_braces:
                if self.is_array(self.flags.mode) and self.opts.keep_array_indentation:
                    self.opts.keep_array_indentation = False
                    self.print_newline()
                    self.opts.keep_array_indentation = True
                else:
                    self.print_newline()

        self.restore_mode()
        self.print_token(current_token)


    def handle_word(self, current_token):
        if current_token.type == 'TK_RESERVED' and self.flags.mode != MODE.ObjectLiteral and \
            current_token.text in ['set', 'get']:
            current_token.type = 'TK_WORD'

        if current_token.type == 'TK_RESERVED' and self.flags.mode == MODE.ObjectLiteral:
            next_token = self.get_token(1)
            if next_token.text == ':':
                current_token.type = 'TK_WORD'

        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            pass
        elif current_token.wanted_newline and \
                not self.is_expression(self.flags.mode) and \
                (self.last_type != 'TK_OPERATOR' or (self.flags.last_text == '--' or self.flags.last_text == '++')) and \
                self.last_type != 'TK_EQUALS' and \
                (self.opts.preserve_newlines or not (self.last_type == 'TK_RESERVED' and self.flags.last_text in ['var', 'let', 'const', 'set', 'get'])):
            self.print_newline()

        if self.flags.do_block and not self.flags.do_while:
            if current_token.type == 'TK_RESERVED' and current_token.text == 'while':
                # do {} ## while ()
                self.output.space_before_token = True
                self.print_token(current_token)
                self.output.space_before_token = True
                self.flags.do_while = True
                return
            else:
                # do {} should always have while as the next word.
                # if we don't see the expected while, recover
                self.print_newline()
                self.flags.do_block = False

        # if may be followed by else, or not
        # Bare/inline ifs are tricky
        # Need to unwind the modes correctly: if (a) if (b) c(); else d(); else e();
        if self.flags.if_block:
            if (not self.flags.else_block) and (current_token.type == 'TK_RESERVED' and current_token.text == 'else'):
                self.flags.else_block = True
            else:
                while self.flags.mode == MODE.Statement:
                    self.restore_mode()

                self.flags.if_block = False

        if current_token.type == 'TK_RESERVED' and (current_token.text == 'case' or (current_token.text == 'default' and self.flags.in_case_statement)):
            self.print_newline()
            if self.flags.case_body or self.opts.jslint_happy:
                self.flags.case_body = False
                self.deindent()
            self.print_token(current_token)
            self.flags.in_case = True
            self.flags.in_case_statement = True
            return

        if current_token.type == 'TK_RESERVED' and current_token.text == 'function':
            if self.flags.last_text in ['}', ';'] or (self.output.just_added_newline() and not self.flags.last_text in ['[', '{', ':', '=', ',']):
                # make sure there is a nice clean space of at least one blank line
                # before a new function definition, except in arrays
                if not self.output.just_added_blankline() and len(current_token.comments_before) == 0:
                    self.print_newline()
                    self.print_newline(True)

            if self.last_type == 'TK_RESERVED' or self.last_type == 'TK_WORD':
                if self.last_type == 'TK_RESERVED' and self.flags.last_text in ['get', 'set', 'new', 'return', 'export']:
                    self.output.space_before_token = True
                elif self.last_type == 'TK_RESERVED' and self.flags.last_text == 'default' and self.last_last_text == 'export':
                    self.output.space_before_token = True
                else:
                    self.print_newline()
            elif self.last_type == 'TK_OPERATOR' or self.flags.last_text == '=':
                # foo = function
                self.output.space_before_token = True
            elif not self.flags.multiline_frame and (self.is_expression(self.flags.mode) or self.is_array(self.flags.mode)):
                # (function
                pass
            else:
                self.print_newline()

        if self.last_type in ['TK_COMMA', 'TK_START_EXPR', 'TK_EQUALS', 'TK_OPERATOR']:
            if not self.start_of_object_property():
                self.allow_wrap_or_preserved_newline(current_token)

        if current_token.type == 'TK_RESERVED' and current_token.text in ['function', 'get', 'set']:
            self.print_token(current_token)
            self.flags.last_word = current_token.text
            return

        prefix = 'NONE'

        if self.last_type == 'TK_END_BLOCK':
            if not (current_token.type == 'TK_RESERVED' and current_token.text in ['else', 'catch', 'finally']):
                prefix = 'NEWLINE'
            else:
                if self.opts.brace_style in ['expand', 'end-expand']:
                    prefix = 'NEWLINE'
                else:
                    prefix = 'SPACE'
                    self.output.space_before_token = True
        elif self.last_type == 'TK_SEMICOLON' and self.flags.mode == MODE.BlockStatement:
            # TODO: Should this be for STATEMENT as well?
            prefix = 'NEWLINE'
        elif self.last_type == 'TK_SEMICOLON' and self.is_expression(self.flags.mode):
            prefix = 'SPACE'
        elif self.last_type == 'TK_STRING':
            prefix = 'NEWLINE'
        elif self.last_type == 'TK_RESERVED' or self.last_type == 'TK_WORD' or \
            (self.flags.last_text == '*' and self.last_last_text == 'function'):
            prefix = 'SPACE'
        elif self.last_type == 'TK_START_BLOCK':
            prefix = 'NEWLINE'
        elif self.last_type == 'TK_END_EXPR':
            self.output.space_before_token = True
            prefix = 'NEWLINE'

        if current_token.type == 'TK_RESERVED' and current_token.text in Tokenizer.line_starters and self.flags.last_text != ')':
            if self.flags.last_text == 'else ' or self.flags.last_text == 'export':
                prefix = 'SPACE'
            else:
                prefix = 'NEWLINE'

        if current_token.type == 'TK_RESERVED' and current_token.text in ['else', 'catch', 'finally']:
            if self.last_type != 'TK_END_BLOCK' \
               or self.opts.brace_style == 'expand' \
               or self.opts.brace_style == 'end-expand':
                self.print_newline()
            else:
                self.output.trim(True)
                # If we trimmed and there's something other than a close block before us
                # put a newline back in.  Handles '} // comment' scenario.
                if self.output.current_line.last() != '}':
                    self.print_newline()

                self.output.space_before_token = True

        elif prefix == 'NEWLINE':
            if self.last_type == 'TK_RESERVED' and self.is_special_word(self.flags.last_text):
                # no newline between return nnn
                self.output.space_before_token = True
            elif self.last_type != 'TK_END_EXPR':
                if (self.last_type != 'TK_START_EXPR' or not (current_token.type == 'TK_RESERVED' and current_token.text in ['var', 'let', 'const'])) and self.flags.last_text != ':':
                    # no need to force newline on VAR -
                    # for (var x = 0...
                    if current_token.type == 'TK_RESERVED' and current_token.text == 'if' and self.flags.last_text == 'else':
                        self.output.space_before_token = True
                    else:
                        self.print_newline()
            elif current_token.type == 'TK_RESERVED' and current_token.text in Tokenizer.line_starters and self.flags.last_text != ')':
                self.print_newline()
        elif self.flags.multiline_frame and self.is_array(self.flags.mode) and self.flags.last_text == ',' and self.last_last_text == '}':
            self.print_newline() # }, in lists get a newline
        elif prefix == 'SPACE':
            self.output.space_before_token = True


        self.print_token(current_token)
        self.flags.last_word = current_token.text

        if current_token.type == 'TK_RESERVED' and current_token.text == 'do':
            self.flags.do_block = True

        if current_token.type == 'TK_RESERVED' and current_token.text == 'if':
            self.flags.if_block = True


    def handle_semicolon(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            # Semicolon can be the start (and end) of a statement
            self.output.space_before_token = False
        while self.flags.mode == MODE.Statement and not self.flags.if_block and not self.flags.do_block:
            self.restore_mode()

        self.print_token(current_token)


    def handle_string(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            # One difference - strings want at least a space before
            self.output.space_before_token = True
        elif self.last_type == 'TK_RESERVED' or self.last_type == 'TK_WORD':
            self.output.space_before_token = True
        elif self.last_type in ['TK_COMMA', 'TK_START_EXPR', 'TK_EQUALS', 'TK_OPERATOR']:
            if not self.start_of_object_property():
                self.allow_wrap_or_preserved_newline(current_token)
        else:
            self.print_newline()

        self.print_token(current_token)


    def handle_equals(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            pass

        if self.flags.declaration_statement:
            # just got an '=' in a var-line, different line breaking rules will apply
            self.flags.declaration_assignment = True

        self.output.space_before_token = True
        self.print_token(current_token)
        self.output.space_before_token = True


    def handle_comma(self, current_token):
        if self.flags.declaration_statement:
            if self.is_expression(self.flags.parent.mode):
                # do not break on comma, for ( var a = 1, b = 2
                self.flags.declaration_assignment = False

            self.print_token(current_token)

            if self.flags.declaration_assignment:
                self.flags.declaration_assignment = False
                self.print_newline(preserve_statement_flags = True)
            else:
                self.output.space_before_token = True

            return

        self.print_token(current_token)

        if self.flags.mode == MODE.ObjectLiteral \
            or (self.flags.mode == MODE.Statement and self.flags.parent.mode ==  MODE.ObjectLiteral):
            if self.flags.mode == MODE.Statement:
                self.restore_mode()

            self.print_newline()
        else:
            # EXPR or DO_BLOCK
            self.output.space_before_token = True


    def handle_operator(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            pass

        if self.last_type == 'TK_RESERVED' and self.is_special_word(self.flags.last_text):
            # return had a special handling in TK_WORD
            self.output.space_before_token = True
            self.print_token(current_token)
            return

        # hack for actionscript's import .*;
        if current_token.text == '*' and self.last_type == 'TK_DOT':
            self.print_token(current_token)
            return


        if current_token.text == ':' and self.flags.in_case:
            self.flags.case_body = True
            self.indent()
            self.print_token(current_token)
            self.print_newline()
            self.flags.in_case = False
            return

        if current_token.text == '::':
            # no spaces around the exotic namespacing syntax operator
            self.print_token(current_token)
            return

        # http://www.ecma-international.org/ecma-262/5.1/#sec-7.9.1
        # if there is a newline between -- or ++ and anything else we should preserve it.
        if current_token.wanted_newline and (current_token.text == '--' or current_token.text == '++'):
            self.print_newline(preserve_statement_flags = True)

        # Allow line wrapping between operators in an expression
        if self.last_type == 'TK_OPERATOR':
            self.allow_wrap_or_preserved_newline(current_token)

        space_before = True
        space_after = True

        if current_token.text in ['--', '++', '!', '~'] \
                or (current_token.text in ['+', '-'] \
                    and (self.last_type in ['TK_START_BLOCK', 'TK_START_EXPR', 'TK_EQUALS', 'TK_OPERATOR'] \
                    or self.flags.last_text in Tokenizer.line_starters or self.flags.last_text == ',')):

            space_before = False
            space_after = False

            if self.flags.last_text == ';' and self.is_expression(self.flags.mode):
                # for (;; ++i)
                #         ^^
                space_before = True

            if self.last_type == 'TK_RESERVED' or self.last_type == 'TK_END_EXPR':
                space_before = True
            elif self.last_type == 'TK_OPERATOR':
                space_before = \
                        (current_token.text in ['--', '-'] and self.flags.last_text in ['--', '-']) or \
                        (current_token.text in ['++', '+'] and self.flags.last_text in ['++', '+'])

            if self.flags.mode == MODE.BlockStatement and self.flags.last_text in ['{', ';']:
                # { foo: --i }
                # foo(): --bar
                self.print_newline()

        elif current_token.text == ':':
            if self.flags.ternary_depth == 0:
                # Colon is invalid javascript outside of ternary and object, but do our best to guess what was meant.
                space_before = False
            else:
                self.flags.ternary_depth -= 1
        elif current_token.text == '?':
            self.flags.ternary_depth += 1
        elif current_token.text == '*' and self.last_type == 'TK_RESERVED' and self.flags.last_text == 'function':
            space_before = False
            space_after = False

        if space_before:
            self.output.space_before_token = True

        self.print_token(current_token)

        if space_after:
            self.output.space_before_token = True



    def handle_block_comment(self, current_token):
        lines = current_token.text.replace('\x0d', '').split('\x0a')
        javadoc = False
        starless = False
        last_indent = ''.join(current_token.whitespace_before)
        last_indent_length = len(last_indent)

        # block comment starts with a new line
        self.print_newline(preserve_statement_flags = True)
        if  len(lines) > 1:
            if not any(l for l in lines[1:] if ( l.strip() == '' or (l.lstrip())[0] != '*')):
                javadoc = True
            elif all(l.startswith(last_indent) or l.strip() == '' for l in lines[1:]):
                starless = True

        # first line always indented
        self.print_token(current_token, lines[0])
        for line in lines[1:]:
            self.print_newline(preserve_statement_flags = True)
            if javadoc:
                # javadoc: reformat and re-indent
                self.print_token(current_token, ' ' + line.strip())
            elif starless and len(line) > last_indent_length:
                # starless: re-indent non-empty content, avoiding trim
                self.print_token(current_token, line[last_indent_length:])
            else:
                # normal comments output raw
                self.output.add_token(line)

        self.print_newline(preserve_statement_flags = True)

    def handle_inline_comment(self, current_token):
        self.output.space_before_token = True
        self.print_token(current_token)
        self.output.space_before_token = True


    def handle_comment(self, current_token):
        if current_token.wanted_newline:
            self.print_newline(preserve_statement_flags = True)

        if not current_token.wanted_newline:
            self.output.trim(True)

        self.output.space_before_token = True
        self.print_token(current_token)
        self.print_newline(preserve_statement_flags = True)


    def handle_dot(self, current_token):
        if self.start_of_statement(current_token):
            # The conditional starts the statement if appropriate.
            pass

        if self.last_type == 'TK_RESERVED' and self.is_special_word(self.flags.last_text):
            self.output.space_before_token = True
        else:
            # allow preserved newlines before dots in general
            # force newlines on dots after close paren when break_chained - for bar().baz()
            self.allow_wrap_or_preserved_newline(current_token,
                self.flags.last_text == ')' and self.opts.break_chained_methods)

        self.print_token(current_token)

    def handle_unknown(self, current_token):
        self.print_token(current_token)
        if current_token.text[-1] == '\n':
            self.print_newline()

    def handle_eof(self, current_token):
        # Unwind any open statements
        while self.flags.mode == MODE.Statement:
            self.restore_mode()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# Using object instead of string to allow for later expansion of info about each line
class OutputLine:
    def __init__(self):
        self.character_count = 0;
        self.line_items = []

    def get_character_count(self):
        return self.character_count

    def get_item_count(self):
        return len(self.line_items)

    def get_output(self):
        return ''.join(self.line_items)

    def last(self):
        if len(self.line_items) > 0:
            return self.line_items[-1]
        else:
            return None

    def push(self, input):
        self.line_items.append(input)
        self.character_count += len(input)

    def remove_indent(self, indent_string, baseIndentString):
        splice_index = 0
        # skip empty lines
        if self.get_item_count() == 0:
            return

        # skip the preindent string if present
        if baseIndentString != '' and \
                 self.line_items[0] == baseIndentString:
            splice_index = 1

        # remove one indent, if present
        if  self.line_items[splice_index] == indent_string:
            self.character_count -= len(self.line_items[splice_index])
            del self.line_items[splice_index]

    def trim(self, indent_string, baseIndentString):
        while self.get_item_count() > 0 \
              and (
                  self.last() == ' '\
                  or self.last() == indent_string \
                  or self.last() == baseIndentString):
            item = line_items.pop()
            self.character_count -= len(item)


class Output:
    def __init__(self, indent_string, baseIndentString):
        self.indent_string = indent_string
        self.baseIndentString = baseIndentString
        self.lines = []
        self.current_line = None
        self.space_before_token = False
        self.add_new_line(True)

    def get_line_number(self):
        return len(self.lines)

    def add_new_line(self, force_newline):
        if len(self.lines) == 1 and self.just_added_newline():
            # no newline on start of file
            return False

        if force_newline or not self.just_added_newline():
            self.current_line = OutputLine()
            self.lines.append(self.current_line)
            return True
        return False

    def get_code(self):
        sweet_code = self.lines[0].get_output()
        if len(self.lines) > 1:
            for line_index in range(1, len(self.lines)):
                sweet_code += '\n' + self.lines[line_index].get_output()

        return re.sub('[\r\n\t ]+$', '', sweet_code)

    def add_indent_string(self, level):
        if self.baseIndentString != '':
            self.current_line.push(self.baseIndentString)

        # Never indent your first output indent at the start of the file
        if len(self.lines) > 1:
            for i in range(level):
                self.current_line.push(self.indent_string)
            return True

        return False

    def add_token(self, printable_token):
        self.add_space_before_token()
        self.current_line.push(printable_token)

    def add_space_before_token(self):
        # make sure only single space gets drawn
        if self.space_before_token and self.current_line.get_item_count() and \
                self.current_line.last() not in [' ', self.indent_string, self.baseIndentString]:
            self.current_line.push(' ')
        self.space_before_token = False

    def remove_redundant_indentation(self, frame):
        # This implementation is effective but has some issues:
        #     - less than great performance due to array splicing
        #     - can cause line wrap to happen too soon due to indent removal
        #           after wrap points are calculated
        # These issues are minor compared to ugly indentation.

        if frame.multiline_frame or frame.mode == MODE.ForInitializer or frame.mode == MODE.Conditional:
            return

        # remove one indent from each line inside this section
        index = frame.start_line_index
        while index < len(self.lines):
            self.lines[index].remove_indent(self.indent_string, self.baseIndentString)
            index += 1

    def trim(self, eat_newlines = False):
        self.current_line.trim(self.indent_string, self.baseIndentString)

        while eat_newlines and len(self.lines) > 1 and \
            self.current_line.get_item_count() == 0:
            self.lines.pop()
            self.current_line = self.lines[-1]
            self.current_line.trim(self.indent_string, self.baseIndentString)


    def just_added_newline(self):
        return self.current_line.get_item_count() == 0

    def just_added_blankline(self):
        if self.just_added_newline():
            if len(self.lines) == 1:
                return True

            line = self.lines[-2]
            return line.get_item_count() == 0

        return False

class Tokenizer:

    whitespace = ["\n", "\r", "\t", " "]
    digit = re.compile('[0-9]')
    punct = ('+ - * / % & ++ -- = += -= *= /= %= == === != !== > < >= <= >> << >>> >>>= >>= <<= && &= | || ! ~ , : ? ^ ^= |= :: =>' \
              + ' <?= <? ?> <%= <% %>').split(' ')

    # Words which always should start on a new line
    line_starters = 'continue,try,throw,return,var,let,const,if,switch,case,default,for,while,break,function,yield,import,export'.split(',')
    reserved_words = line_starters + ['do', 'in', 'else', 'get', 'set', 'new', 'catch', 'finally', 'typeof']

    def __init__ (self, input, opts, indent_string):
        self.input = input
        self.opts = opts
        self.indent_string = indent_string
        self.acorn = Acorn()


    def tokenize(self):
        self.in_html_comment = False
        self.parser_pos = 0
        self.tokens = []

        next = None
        last = None
        open = None
        open_stack = []
        comments = []

        while not (not last == None and last.type == 'TK_EOF'):
            token_values = self.__tokenize_next()
            next = Token(token_values[1], token_values[0], self.n_newlines, self.whitespace_before_token)

            while next.type == 'TK_INLINE_COMMENT' or next.type == 'TK_COMMENT' or \
                next.type == 'TK_BLOCK_COMMENT' or next.type == 'TK_UNKNOWN':
                comments.append(next)
                token_values = self.__tokenize_next()
                next = Token(token_values[1], token_values[0], self.n_newlines, self.whitespace_before_token)

            if len(comments) > 0:
                next.comments_before = comments
                comments = []

            if next.type == 'TK_START_BLOCK' or next.type == 'TK_START_EXPR':
                next.parent = last
                open = next
                open_stack.append(next)
            elif (next.type == 'TK_END_BLOCK' or next.type == 'TK_END_EXPR') and \
                (not open == None and ( \
                    (next.text == ']' and open.text == '[') or \
                    (next.text == ')' and open.text == '(') or \
                    (next.text == '}' and open.text == '}'))):
                next.parent = open.parent
                open = open_stack.pop()

            self.tokens.append(next)
            last = next
        return self.tokens


    def __tokenize_next(self):

        self.n_newlines = 0
        self.whitespace_before_token = []

        if self.parser_pos >= len(self.input):
            return '', 'TK_EOF'

        if len(self.tokens) > 0:
            last_token = self.tokens[-1]
        else:
            # For the sake of tokenizing we can pretend that there was on open brace to start
            last_token = Token('TK_START_BLOCK', '{')

        c = self.input[self.parser_pos]
        self.parser_pos += 1

        while c in self.whitespace:
            if c == '\n':
                self.n_newlines += 1
                self.whitespace_before_token = []
            elif c == self.indent_string:
                self.whitespace_before_token.append(self.indent_string)
            elif c != '\r':
                self.whitespace_before_token.append(' ')

            if self.parser_pos >= len(self.input):
                return '', 'TK_EOF'

            c = self.input[self.parser_pos]
            self.parser_pos += 1

        if self.digit.match(c):
            allow_decimal = True
            allow_e = True
            local_digit = self.digit

            if c == '0' and self.parser_pos < len(self.input) and re.match('[Xx]', self.input[self.parser_pos]):
                # switch to hex number, no decimal or e, just hex digits
                allow_decimal = False
                allow_e = False
                c += self.input[self.parser_pos]
                self.parser_pos += 1
                local_digit = re.compile('[0123456789abcdefABCDEF]')
            else:
                # we know this first loop will run.  It keeps the logic simpler.
                c = ''
                self.parser_pos -= 1

            # Add the digits
            while self.parser_pos < len(self.input) and local_digit.match(self.input[self.parser_pos]):
                c += self.input[self.parser_pos]
                self.parser_pos += 1

                if allow_decimal and self.parser_pos < len(self.input) and self.input[self.parser_pos] == '.':
                    c += self.input[self.parser_pos]
                    self.parser_pos += 1
                    allow_decimal = False

                if allow_e and self.parser_pos < len(self.input) and re.match('[Ee]', self.input[self.parser_pos]):
                    c += self.input[self.parser_pos]
                    self.parser_pos += 1

                    if self.parser_pos < len(self.input) and re.match('[+-]', self.input[self.parser_pos]):
                        c += self.input[self.parser_pos]
                        self.parser_pos += 1

                    allow_e = False
                    allow_decimal = False

            return c, 'TK_WORD'

        if self.acorn.isIdentifierStart(ord(self.input[self.parser_pos-1])):
            if self.parser_pos < len(self.input):
                while self.acorn.isIdentifierChar(ord(self.input[self.parser_pos])):
                    c = c + self.input[self.parser_pos]
                    self.parser_pos += 1
                    if self.parser_pos == len(self.input):
                        break

            if not (last_token.type == 'TK_DOT' \
                        or (last_token.type == 'TK_RESERVED' and last_token.text in ['set', 'get'])) \
                    and c in self.reserved_words:
                if c == 'in': # in is an operator, need to hack
                    return c, 'TK_OPERATOR'

                return c, 'TK_RESERVED'

            return c, 'TK_WORD'

        if c in '([':
            return c, 'TK_START_EXPR'

        if c in ')]':
            return c, 'TK_END_EXPR'

        if c == '{':
            return c, 'TK_START_BLOCK'

        if c == '}':
            return c, 'TK_END_BLOCK'

        if c == ';':
            return c, 'TK_SEMICOLON'

        if c == '/':
            comment = ''
            inline_comment = True
            if self.input[self.parser_pos] == '*': # peek /* .. */ comment
                self.parser_pos += 1
                if self.parser_pos < len(self.input):
                    while not (self.input[self.parser_pos] == '*' and \
                               self.parser_pos + 1 < len(self.input) and \
                               self.input[self.parser_pos + 1] == '/')\
                          and self.parser_pos < len(self.input):
                        c = self.input[self.parser_pos]
                        comment += c
                        if c in '\r\n':
                            inline_comment = False
                        self.parser_pos += 1
                        if self.parser_pos >= len(self.input):
                            break
                self.parser_pos += 2
                if inline_comment and self.n_newlines == 0:
                    return '/*' + comment + '*/', 'TK_INLINE_COMMENT'
                else:
                    return '/*' + comment + '*/', 'TK_BLOCK_COMMENT'

            if self.input[self.parser_pos] == '/': # peek // comment
                comment = c
                while self.input[self.parser_pos] not in '\r\n':
                    comment += self.input[self.parser_pos]
                    self.parser_pos += 1
                    if self.parser_pos >= len(self.input):
                        break

                return comment, 'TK_COMMENT'

        if c == '`' or c == "'" or c == '"' or \
            ( \
                (c == '/') or \
                (self.opts.e4x and c == "<" and re.match('^<(!\[CDATA\[[\s\S]*?\]\]|[-a-zA-Z:0-9_.]+|\{[^{}]*\})\s*([-a-zA-Z:0-9_.]+=(\{[^{}]*\}|"[^"]*"|\'[^\']*\')\s*)*\/?\s*>', self.input[self.parser_pos - 1:])) \
            ) and ( \
                (last_token.type == 'TK_RESERVED' and last_token.text in ['return', 'case', 'throw', 'else', 'do', 'typeof', 'yield']) or \
                (last_token.type == 'TK_END_EXPR' and last_token.text == ')' and \
                            last_token.parent and last_token.parent.type == 'TK_RESERVED' and last_token.parent.text in ['if', 'while', 'for']) or \
                (last_token.type in ['TK_COMMENT', 'TK_START_EXPR', 'TK_START_BLOCK', 'TK_END_BLOCK', 'TK_OPERATOR', \
                                   'TK_EQUALS', 'TK_EOF', 'TK_SEMICOLON', 'TK_COMMA'])):
            sep = c
            esc = False
            esc1 = 0
            esc2 = 0
            resulting_string = c
            in_char_class = False

            if sep == '/':
                # handle regexp
                in_char_class = False
                while self.parser_pos < len(self.input) and \
                        (esc or in_char_class or self.input[self.parser_pos] != sep) and \
                        not self.acorn.newline.match(self.input[self.parser_pos]):
                    resulting_string += self.input[self.parser_pos]
                    if not esc:
                        esc = self.input[self.parser_pos] == '\\'
                        if self.input[self.parser_pos] == '[':
                            in_char_class = True
                        elif self.input[self.parser_pos] == ']':
                            in_char_class = False
                    else:
                        esc = False
                    self.parser_pos += 1

            elif self.opts.e4x and sep == '<':
                # handle e4x xml literals
                xmlRegExp = re.compile('<(\/?)(!\[CDATA\[[\s\S]*?\]\]|[-a-zA-Z:0-9_.]+|\{[^{}]*\})\s*([-a-zA-Z:0-9_.]+=(\{[^{}]*\}|"[^"]*"|\'[^\']*\')\s*)*(\/?)\s*>')
                xmlStr = self.input[self.parser_pos - 1:]
                match = xmlRegExp.match(xmlStr)
                if match:
                    rootTag = match.group(2)
                    depth = 0
                    while (match):
                        isEndTag = match.group(1)
                        tagName = match.group(2)
                        isSingletonTag = (match.groups()[-1] != "") or (match.group(2)[0:8] == "![CDATA[")
                        if tagName == rootTag and not isSingletonTag:
                            if isEndTag:
                                depth -= 1
                            else:
                                depth += 1

                        if depth <= 0:
                            break

                        match = xmlRegExp.search(xmlStr, match.end())

                    if match:
                        xmlLength = match.end() # + len(match.group())
                    else:
                        xmlLength = len(xmlStr)

                    self.parser_pos += xmlLength - 1
                    return xmlStr[:xmlLength], 'TK_STRING'

            else:
                # handle string
                while self.parser_pos < len(self.input) and \
                        (esc or (self.input[self.parser_pos] != sep and
                            (sep == '`' or not self.acorn.newline.match(self.input[self.parser_pos])))):
                    resulting_string += self.input[self.parser_pos]
                    if esc1 and esc1 >= esc2:
                        try:
                            esc1 = int(resulting_string[-esc2:], 16)
                        except Exception:
                            esc1 = False
                        if esc1 and esc1 >= 0x20 and esc1 <= 0x7e:
                            esc1 = chr(esc1)
                            resulting_string = resulting_string[:-2 - esc2]
                            if esc1 == sep or esc1 == '\\':
                                    resulting_string += '\\'
                            resulting_string += esc1
                        esc1 = 0
                    if esc1:
                        esc1 += 1
                    elif not esc:
                        esc = self.input[self.parser_pos] == '\\'
                    else:
                        esc = False
                        if self.opts.unescape_strings:
                            if self.input[self.parser_pos] == 'x':
                                esc1 += 1
                                esc2 = 2
                            elif self.input[self.parser_pos] == 'u':
                                esc1 += 1
                                esc2 = 4
                    self.parser_pos += 1


            if self.parser_pos < len(self.input) and self.input[self.parser_pos] == sep:
                resulting_string += sep
                self.parser_pos += 1

                if sep == '/':
                    # regexps may have modifiers /regexp/MOD, so fetch those too
                    # Only [gim] are valid, but if the user puts in garbage, do what we can to take it.
                    while self.parser_pos < len(self.input) and self.acorn.isIdentifierStart(ord(self.input[self.parser_pos])):
                        resulting_string += self.input[self.parser_pos]
                        self.parser_pos += 1

            return resulting_string, 'TK_STRING'

        if c == '#':

            # she-bang
            if len(self.tokens) == 0 and len(self.input) > self.parser_pos and self.input[self.parser_pos] == '!':
                resulting_string = c
                while self.parser_pos < len(self.input) and c != '\n':
                    c = self.input[self.parser_pos]
                    resulting_string += c
                    self.parser_pos += 1
                return resulting_string.strip() + '\n', 'TK_UNKNOWN'


            # Spidermonkey-specific sharp variables for circular references
            # https://developer.mozilla.org/En/Sharp_variables_in_JavaScript
            # http://mxr.mozilla.org/mozilla-central/source/js/src/jsscan.cpp around line 1935
            sharp = '#'
            if self.parser_pos < len(self.input) and self.digit.match(self.input[self.parser_pos]):
                while True:
                    c = self.input[self.parser_pos]
                    sharp += c
                    self.parser_pos += 1
                    if self.parser_pos >= len(self.input)  or c == '#' or c == '=':
                        break
            if c == '#' or self.parser_pos >= len(self.input):
                pass
            elif self.input[self.parser_pos] == '[' and self.input[self.parser_pos + 1] == ']':
                sharp += '[]'
                self.parser_pos += 2
            elif self.input[self.parser_pos] == '{' and self.input[self.parser_pos + 1] == '}':
                sharp += '{}'
                self.parser_pos += 2
            return sharp, 'TK_WORD'

        if c == '<' and self.input[self.parser_pos - 1 : self.parser_pos + 3] == '<!--':
            self.parser_pos += 3
            c = '<!--'
            while self.parser_pos < len(self.input) and self.input[self.parser_pos] != '\n':
                c += self.input[self.parser_pos]
                self.parser_pos += 1
            self.in_html_comment = True
            return c, 'TK_COMMENT'

        if c == '-' and self.in_html_comment and self.input[self.parser_pos - 1 : self.parser_pos + 2] == '-->':
            self.in_html_comment = False
            self.parser_pos += 2
            return '-->', 'TK_COMMENT'

        if c == '.':
            return c, 'TK_DOT'

        if c in self.punct:
            while self.parser_pos < len(self.input) and c + self.input[self.parser_pos] in self.punct:
                c += self.input[self.parser_pos]
                self.parser_pos += 1
                if self.parser_pos >= len(self.input):
                    break

            if c == ',':
                return c, 'TK_COMMA'
            if c == '=':
                return c, 'TK_EQUALS'

            return c, 'TK_OPERATOR'

        return c, 'TK_UNKNOWN'


def main():

    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "s:c:o:dEPjabkil:xhtfvXnw:",
            ['indent-size=','indent-char=','outfile=', 'disable-preserve-newlines',
            'space-in-paren', 'space-in-empty-paren', 'jslint-happy', 'space-after-anon-function',
            'brace-style=', 'keep-array-indentation', 'indent-level=', 'unescape-strings', 'help',
            'usage', 'stdin', 'eval-code', 'indent-with-tabs', 'keep-function-indentation', 'version',
            'e4x', 'end-with-newline','wrap-line-length'])
    except getopt.GetoptError as ex:
        print(ex, file=sys.stderr)
        return usage(sys.stderr)

    js_options = default_options()

    file = None
    outfile = 'stdout'
    if len(args) == 1:
        file = args[0]

    for opt, arg in opts:
        if opt in ('--keep-array-indentation', '-k'):
            js_options.keep_array_indentation = True
        if opt in ('--keep-function-indentation','-f'):
            js_options.keep_function_indentation = True
        elif opt in ('--outfile', '-o'):
            outfile = arg
        elif opt in ('--indent-size', '-s'):
            js_options.indent_size = int(arg)
        elif opt in ('--indent-char', '-c'):
            js_options.indent_char = arg
        elif opt in ('--indent-with-tabs', '-t'):
            js_options.indent_with_tabs = True
        elif opt in ('--disable-preserve-newlines', '-d'):
            js_options.preserve_newlines = False
        elif opt in ('--space-in-paren', '-P'):
            js_options.space_in_paren = True
        elif opt in ('--space-in-empty-paren', '-E'):
            js_options.space_in_empty_paren = True
        elif opt in ('--jslint-happy', '-j'):
            js_options.jslint_happy = True
        elif opt in ('--space_after_anon_function', '-a'):
            js_options.space_after_anon_function = True
        elif opt in ('--eval-code'):
            js_options.eval_code = True
        elif opt in ('--brace-style', '-b'):
            js_options.brace_style = arg
        elif opt in ('--unescape-strings', '-x'):
            js_options.unescape_strings = True
        elif opt in ('--e4x', '-X'):
            js_options.e4x = True
        elif opt in ('--end-with-newline', '-n'):
            js_options.end_with_newline = True
        elif opt in ('--wrap-line-length ', '-w'):
            js_options.wrap_line_length = int(arg)
        elif opt in ('--stdin', '-i'):
            file = '-'
        elif opt in ('--version', '-v'):
            return print(__version__)
        elif opt in ('--help', '--usage', '-h'):
            return usage()


    if not file:
        print("Must define at least one file.", file=sys.stderr)
        return usage(sys.stderr)
    else:
        try:
            if outfile == 'stdout':
                sys.stdout.write(beautify_file(file, js_options))
            else:
                mkdir_p(os.path.dirname(outfile))
                with open(outfile, 'w') as f:
                    f.write(beautify_file(file, js_options))
        except Exception as ex:
            print(ex, file=sys.stderr)
            return 1

    # Success
    return 0
