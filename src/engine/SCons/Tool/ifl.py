"""engine.SCons.Tool.icc

Tool-specific initialization for the Intel Fortran compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# Copyright (c) 2001, 2002 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import string

import SCons.Action
import SCons.Tool
import SCons.Errors

F77Suffixes = ['.f', '.for', '.FOR']
F77PPSuffixes = ['.fpp', '.FPP']
if os.path.normcase('.f') == os.path.normcase('.F'):
    F77Suffixes.append('.F')
else:
    F77PPSuffixes.append('.F')

def generate(env, platform):
    """Add Builders and construction variables for ifl to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in F77Suffixes:
        static_obj.add_action(suffix, SCons.Defaults.F77Action)
        shared_obj.add_action(suffix, SCons.Defaults.ShF77Action)

    for suffix in F77PPSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.F77PPAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShF77PPAction)

    env['F77']        = 'ifl'
    env['F77FLAGS']   = ''
    env['F77COM']     = '$F77 $F77FLAGS $_F77INCFLAGS /c $SOURCES /Fo$TARGET'
    env['F77PPCOM']   = '$F77 $F77FLAGS $CPPFLAGS $_F77INCFLAGS /c $SOURCES /Fo$TARGET'
    env['SHF77']      = '$F77'
    env['SHF77FLAGS'] = '$F77FLAGS'
    env['SHF77COM']   = '$SHF77 $SHF77FLAGS $_F77INCFLAGS /c $SOURCES /Fo$TARGET'
    env['SHF77PPCOM'] = '$SHF77 $SHF77FLAGS $CPPFLAGS $_F77INCFLAGS /c $SOURCES /Fo$TARGET'

def exists():
    return SCons.Util.WhereIs('ifl')
