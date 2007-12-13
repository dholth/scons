#!/usr/bin/env python
#
# __COPYRIGHT__
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

"""
See if the packaging tool is able to build multiple packages at once.

TODO: test if the packages are clean versions (i.e. do not contain files
      added by different packager runs)
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

zip = test.detect('ZIP', 'zip')

if not zip:
    test.skip_test('zip not found, skipping test\n')

test.subdir('src')

test.write( [ 'src', 'main.c' ], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
""")

test.write('SConstruct', """
Program( 'src/main.c' )
env=Environment(tools=['default', 'packaging'])
env.Package( PACKAGETYPE  = ['src_zip', 'src_targz'],
             target       = ['src.zip', 'src.tar.gz'],
             PACKAGEROOT  = 'test',
             source       = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(arguments='', stderr = None)

test.must_exist( 'src.zip' )
test.must_exist( 'src.tar.gz' )

test.write('SConstruct', """
Program( 'src/main.c' )
env=Environment(tools=['default', 'packaging'])
env.Package( PACKAGETYPE  = ['src_zip', 'src_targz'],
             NAME = "src", VERSION = "1.0",
             PACKAGEROOT  = 'test',
             source       = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(arguments='', stderr = None)

test.must_exist( 'src-1.0.zip' )
test.must_exist( 'src-1.0.tar.gz' )

test.write('SConstruct', """
Program( 'src/main.c' )
env=Environment(tools=['default', 'packaging'])
env.Package( PACKAGETYPE  = ['src_zip', 'src_targz'],
             NAME = "src", VERSION = "1.0",
             PACKAGEROOT  = 'test',
             source       = [ 'src/main.c', 'SConstruct' ],
             target       = 'src.zip' )
""")

test.run(arguments='', stderr = None)

test.must_exist( 'src.zip' )
test.must_exist( 'src-1.0.tar.gz' )



test.pass_test()
