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

import os.path
import TestSCons

test = TestSCons.TestSCons()

test.subdir('work', 'repository', ['repository', 'src'])

work_aaa = test.workpath('work', 'aaa')
work_bbb = test.workpath('work', 'bbb')
work_ccc = test.workpath('work', 'ccc')
work_src_xxx = test.workpath('work', 'src', 'xxx')
work_src_yyy = test.workpath('work', 'src', 'yyy')

opts = "-Y " + test.workpath('repository')

test.write(['repository', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    print 'cat(%s) > %s' % (source, target)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()

env = Environment(BUILDERS={'Build':Builder(action=cat)})
env.Build('aaa.out', 'aaa.in')
env.Build('bbb.out', 'bbb.in')
env.Build('ccc.out', 'ccc.in')
SConscript('src/SConscript', "env")
""")

test.write(['repository', 'aaa.in'], "repository/aaa.in\n")
test.write(['repository', 'bbb.in'], "repository/bbb.in\n")
test.write(['repository', 'ccc.in'], "repository/ccc.in\n")

test.write(['repository', 'src', 'SConscript'], """
Import("env")
env.Build('xxx.out', 'xxx.in')
env.Build('yyy.out', 'yyy.in')
""")

test.write(['repository', 'src', 'xxx.in'], "repository/src/xxx.in\n")
test.write(['repository', 'src', 'yyy.in'], "repository/src/yyy.in\n")

#
# Make the repository non-writable,
# so we'll detect if we try to write into it accidentally.
test.writable('repository', 0)

#
test.run(chdir = 'work', options = opts, arguments = 'aaa.out')

test.fail_test(test.read(['work', 'aaa.out']) != "repository/aaa.in\n")
test.fail_test(os.path.exists(test.workpath('work', 'bbb.out')))
test.fail_test(os.path.exists(test.workpath('work', 'ccc.out')))
test.fail_test(os.path.exists(test.workpath('work', 'src', 'xxx.out')))
test.fail_test(os.path.exists(test.workpath('work', 'src', 'yyy.out')))

test.run(chdir = 'work', options = opts, arguments = 'bbb.out src')

test.fail_test(test.read(['work', 'bbb.out']) != "repository/bbb.in\n")
test.fail_test(os.path.exists(test.workpath('work', 'ccc.out')))
test.fail_test(test.read(['work', 'src', 'xxx.out']) != "repository/src/xxx.in\n")
test.fail_test(test.read(['work', 'src', 'yyy.out']) != "repository/src/yyy.in\n")

#
test.run(chdir = 'work', options = opts, arguments = '.')

test.fail_test(test.read(['work', 'ccc.out']) != "repository/ccc.in\n")

#
test.pass_test()
