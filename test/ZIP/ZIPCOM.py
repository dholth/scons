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
Test the ability to configure the $ZIPCOM construction variable.
"""

import os
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()



test.write('myzip.py', r"""
import sys
outfile = open(sys.argv[1], 'wb')
infile = open(sys.argv[2], 'rb')
for l in filter(lambda l: l != '/*zip*/\n', infile.readlines()):
    outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(TOOLS = ['zip'],
                  ZIPCOM = r'%(python)s myzip.py $TARGET $SOURCE')
env.Zip('test1.zip', 'test1.in')
""" % locals())

test.write('test1.in', """\
test1.in
/*zip*/
""")

test.run()

test.must_match('test1.zip', "test1.in\n")



test.pass_test()