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

"""
This tests the -j command line option, and the num_jobs
SConscript settable option.
"""
from builtins import map

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import sys

import TestSCons


_python_ = TestSCons._python_

try:
    import threading
except ImportError:
    # if threads are not supported, then
    # there is nothing to test
    TestCmd.no_result()
    sys.exit()


test = TestSCons.TestSCons()

test.write('build.py', r"""
import time
import sys
file = open(sys.argv[1], 'wb')
file.write(str(time.time()) + '\n')
time.sleep(1)
file.write(str(time.time()))
file.close()
""")

test.subdir('foo')

test.write(['foo','foo.in'], r"""
foo you
""")

test.write('SConstruct', """
MyBuild = Builder(action = r'%(_python_)s build.py $TARGETS')
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.Tool('install')
env.MyBuild(target = 'f1', source = 'f1.in')
env.MyBuild(target = 'f2', source = 'f2.in')

def copyn(env, target, source):
    import shutil
    import time
    time.sleep(1)
    for t in target:
        shutil.copy(str(source[0]), str(t))

t = env.Command(target=['foo/foo1.out', 'foo/foo2.out'],
                source='foo/foo.in',
                action=copyn)
env.Install('out', t)
""" % locals())

def RunTest(args, extra):
    """extra is used to make scons rebuild the output file"""
    test.write('f1.in', 'f1.in'+extra)
    test.write('f2.in', 'f2.in'+extra)

    test.run(arguments = args)

    str = test.read("f1")
    start1,finish1 = list(map(float, str.split("\n")))

    str = test.read("f2")
    start2,finish2 = list(map(float, str.split("\n")))

    return start2, finish1

# Test 2 parallel jobs.
# fail if the second file was not started
# before the first one was finished.
start2, finish1 = RunTest('-j 2 f1 f2', "first")
test.fail_test(not (start2 < finish1))

# re-run the test with the same input, fail if we don't
# get back the same times, which would indicate that
# SCons rebuilt the files even though nothing changed
s2, f1 = RunTest('-j 2 f1 f2', "first")
test.fail_test(start2 != s2)
test.fail_test(finish1 != f1)

# Test a single serial job.
# fail if the second file was started
# before the first one was finished
start2, finish1 = RunTest('f1 f2', "second")
test.fail_test(start2 < finish1)

# Make sure that a parallel build using a list builder
# succeeds.
test.run(arguments='-j 2 out')

if sys.platform != 'win32':
    # Test breaks on win32 when using real subprocess is not the only
    # package to import threading
    #
    # Test that we fall back and warn properly if there's no threading.py
    # module (simulated), which is the case if this version of Python wasn't
    # built with threading support.

    test.subdir('pythonlib')

    test.write(['pythonlib', 'threading.py'], "raise ImportError\n")

    save_pythonpath = os.environ.get('PYTHONPATH', '')
    os.environ['PYTHONPATH'] = test.workpath('pythonlib')

    #start2, finish1 = RunTest('-j 2 f1, f2', "fifth")

    test.write('f1.in', 'f1.in pythonlib\n')
    test.write('f2.in', 'f2.in pythonlib\n')

    test.run(arguments = "-j 2 f1 f2", stderr=None)

    warn = """scons: warning: parallel builds are unsupported by this version of Python;
\tignoring -j or num_jobs option."""
    test.must_contain_all_lines(test.stderr(), [warn])

    str = test.read("f1")
    start1,finish1 = list(map(float, str.split("\n")))

    str = test.read("f2")
    start2,finish2 = list(map(float, str.split("\n")))

    test.fail_test(start2 < finish1)

    os.environ['PYTHONPATH'] = save_pythonpath


# Test SetJobs() with no -j:
test.write('SConstruct', """
MyBuild = Builder(action = r'%(_python_)s build.py $TARGETS')
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.Tool('install')
env.MyBuild(target = 'f1', source = 'f1.in')
env.MyBuild(target = 'f2', source = 'f2.in')

def copyn(env, target, source):
    import shutil
    import time
    time.sleep(1)
    for t in target:
        shutil.copy(str(source[0]), str(t))

t = env.Command(target=['foo/foo1.out', 'foo/foo2.out'], source='foo/foo.in', action=copyn)
env.Install('out', t)

assert GetOption('num_jobs') == 1
SetOption('num_jobs', 2)
assert GetOption('num_jobs') == 2
""" % locals())

# This should be a parallel build because the SConscript sets jobs to 2.
# fail if the second file was not started
# before the first one was finished
start2, finish1 = RunTest('f1 f2', "third")
test.fail_test(not (start2 < finish1))

# Test SetJobs() with -j:
test.write('SConstruct', """
MyBuild = Builder(action = r'%(_python_)s build.py $TARGETS')
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.Tool('install')
env.MyBuild(target = 'f1', source = 'f1.in')
env.MyBuild(target = 'f2', source = 'f2.in')

def copyn(env, target, source):
    import shutil
    import time
    time.sleep(1)
    for t in target:
        shutil.copy(str(source[0]), str(t))

t = env.Command(target=['foo/foo1.out', 'foo/foo2.out'], source='foo/foo.in', action=copyn)
env.Install('out', t)

assert GetOption('num_jobs') == 1
SetOption('num_jobs', 2)
assert GetOption('num_jobs') == 1
""" % locals())

# This should be a serial build since -j 1 overrides the call to SetJobs().
# fail if the second file was started
# before the first one was finished
start2, finish1 = RunTest('-j 1 f1 f2', "fourth")
test.fail_test(start2 < finish1)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
