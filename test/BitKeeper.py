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
Test fetching source files from BitKeeper.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

bk = test.where_is('bk')
if not bk:
    print "Could not find BitKeeper, skipping test(s)."
    test.pass_test(1)

try:
    login = os.getlogin()
except AttributeError:
    try:
        login = os.environ['USER']
    except KeyError:
        login = 'USER'

host = os.uname()[1]

email = "%s@%s" % (login, host)

test.subdir('BitKeeper', 'import', ['import', 'sub'], 'work1', 'work2')

# Set up the BitKeeper repository.
bkroot = test.workpath('BitKeeper')
bk_conf = test.workpath('bk.conf')

# BitKeeper's licensing restrictions require a configuration file that
# specifies you're not using it multi-user.  This seems to be the
# minimal configuration that satisfies these requirements.
test.write(bk_conf, """\
description:test project 'foo'
logging:none
email:%s
single_user:%s
single_host:%s
""" % (email, login, host))

# Plus, we need to set the external environment variable that gets it to
# shut up and not prompt us to accept the license.
os.environ['BK_LICENSE'] = 'ACCEPTED'

test.run(chdir = bkroot,
         program = bk,
         arguments = 'setup -f -c %s foo' % bk_conf)

test.write(['import', 'aaa.in'], "import/aaa.in\n")
test.write(['import', 'bbb.in'], "import/bbb.in\n")
test.write(['import', 'ccc.in'], "import/ccc.in\n")

test.write(['import', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")

test.write(['import', 'sub', 'ddd.in'], "import/sub/ddd.in\n")
test.write(['import', 'sub', 'eee.in'], "import/sub/eee.in\n")
test.write(['import', 'sub', 'fff.in'], "import/sub/fff.in\n")

test.run(chdir = 'import',
         program = bk,
         arguments = 'import -q -f -tplain . %s/foo' % bkroot)

# Test the most straightforward BitKeeper checkouts, using the module name.
test.write(['work1', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'foo/aaa.in')
env.Cat('bbb.out', 'foo/bbb.in')
env.Cat('ccc.out', 'foo/ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.BitKeeper(r'%s'))
SConscript('foo/sub/SConscript', "env")
""" % bkroot)

test.subdir(['work1', 'foo'])
test.write(['work1', 'foo', 'bbb.in'], "work1/foo/bbb.in\n")

test.subdir(['work1', 'foo', 'sub'])
test.write(['work1', 'foo', 'sub', 'eee.in'], "work1/foo/sub/eee.in\n")

test.run(chdir = 'work1',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
bk get -p %s/foo/sub/SConscript > foo/sub/SConscript
""" % (bkroot),
                                   build_str = """\
bk get -p %s/foo/aaa.in > foo/aaa.in
cat("aaa.out", "foo/aaa.in")
cat("bbb.out", "foo/bbb.in")
bk get -p %s/foo/ccc.in > foo/ccc.in
cat("ccc.out", "foo/ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
bk get -p %s/foo/sub/ddd.in > foo/sub/ddd.in
cat("foo/sub/ddd.out", "foo/sub/ddd.in")
cat("foo/sub/eee.out", "foo/sub/eee.in")
bk get -p %s/foo/sub/fff.in > foo/sub/fff.in
cat("foo/sub/fff.out", "foo/sub/fff.in")
cat("foo/sub/all", ["foo/sub/ddd.out", "foo/sub/eee.out", "foo/sub/fff.out"])
""" % (bkroot, bkroot, bkroot, bkroot)),
         stderr = """\
%s/foo/sub/SConscript 1.1: 5 lines
%s/foo/aaa.in 1.1: 1 lines
%s/foo/ccc.in 1.1: 1 lines
%s/foo/sub/ddd.in 1.1: 1 lines
%s/foo/sub/fff.in 1.1: 1 lines
""" % (bkroot, bkroot, bkroot, bkroot, bkroot))

test.fail_test(test.read(['work1', 'all']) != "import/aaa.in\nwork1/foo/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work1', 'foo', 'sub', 'all']) != "import/sub/ddd.in\nwork1/foo/sub/eee.in\nimport/sub/fff.in\n")

# Test BitKeeper checkouts when the module name is specified.
test.write(['work2', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  BITKEEPERFLAGS='-q')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.BitKeeper(r'%s', 'foo'))
SConscript('sub/SConscript', "env")
""" % bkroot)

test.write(['work2', 'bbb.in'], "work2/bbb.in\n")

test.subdir(['work2', 'sub'])
test.write(['work2', 'sub', 'eee.in'], "work2/sub/eee.in\n")

test.run(chdir = 'work2',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
bk get -q -p %s/foo/sub/SConscript > sub/SConscript
""" % (bkroot),
                                   build_str = """\
bk get -q -p %s/foo/aaa.in > aaa.in
cat("aaa.out", "aaa.in")
cat("bbb.out", "bbb.in")
bk get -q -p %s/foo/ccc.in > ccc.in
cat("ccc.out", "ccc.in")
cat("all", ["aaa.out", "bbb.out", "ccc.out"])
bk get -q -p %s/foo/sub/ddd.in > sub/ddd.in
cat("sub/ddd.out", "sub/ddd.in")
cat("sub/eee.out", "sub/eee.in")
bk get -q -p %s/foo/sub/fff.in > sub/fff.in
cat("sub/fff.out", "sub/fff.in")
cat("sub/all", ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
""" % (bkroot, bkroot, bkroot, bkroot)))

test.fail_test(test.read(['work2', 'all']) != "import/aaa.in\nwork2/bbb.in\nimport/ccc.in\n")

test.fail_test(test.read(['work2', 'sub', 'all']) != "import/sub/ddd.in\nwork2/sub/eee.in\nimport/sub/fff.in\n")

test.pass_test()
