#
# Copyright (c) 2001 Steven Knight
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

import sys
import unittest

import SCons.Taskmaster
import SCons.Errors


built = None
executed = None

class Node:
    def __init__(self, name, kids = [], scans = []):
        self.name = name
        self.kids = kids
        self.scans = scans
        self.builder = Node.build
        self.bsig = None
        self.csig = None
        self.state = None
        self.parents = []

        for kid in kids:
            kid.parents.append(self)

    def build(self):
        global built
        built = self.name + " built"

    def children(self):
	return self.kids

    def scan(self):
        self.kids = self.kids + self.scans
        for scan in self.scans:
            scan.parents.append(self)
        self.scans = []
  
    def get_parents(self):
        return self.parents

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_bsig(self, bsig):
        self.bsig = bsig

    def set_csig(self, csig):
        self.csig = csig
  
    def children_are_executed(self):
        return reduce(lambda x,y: ((y.get_state() == SCons.Node.executed
                                   or y.get_state() == SCons.Node.up_to_date)
                                   and x),
                      self.children(),
                      1)
    def __str__(self):
        return self.name


class TaskmasterTestCase(unittest.TestCase):

    def test_next_task(self):
	"""Test fetching the next task
	"""
	global built
        
	n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1, n1])
        t = tm.next_task()
        t.executed()
        t = tm.next_task()
        assert t == None

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        
	tm = SCons.Taskmaster.Taskmaster([n3])

        t = tm.next_task()
        t.execute()
        assert built == "n1 built"
        t.executed()

        t = tm.next_task()
        t.execute()
        assert built == "n2 built"
        t.executed()

        t = tm.next_task()
        t.execute()
        assert built == "n3 built"
        t.executed()

        assert tm.next_task() == None

        built = "up to date: "
        top_node = n3

        class MyCalc(SCons.Taskmaster.Calc):
            def current(self, node, sig):
                return 1

        class MyTask(SCons.Taskmaster.Task):
            def execute(self):
                global built
                if self.targets[0].get_state() == SCons.Node.up_to_date:
                    if self.top:
                        built = self.targets[0].name + " up-to-date top"
                    else:
                        built = self.targets[0].name + " up-to-date"
                else:
                    self.targets[0].build()

        n1.set_state(None)
        n2.set_state(None)
        n3.set_state(None)
        tm = SCons.Taskmaster.Taskmaster(targets = [n3],
                                         tasker = MyTask, calc = MyCalc())

        t = tm.next_task()
        t.execute()
        assert built == "n1 up-to-date"
        t.executed()

        t = tm.next_task()
        t.execute()
        assert built == "n2 up-to-date"
        t.executed()

        t = tm.next_task()
        t.execute()
        assert built == "n3 up-to-date top"
        t.executed()

	assert tm.next_task() == None


        n1 = Node("n1")
	n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        n4 = Node("n4")
        n5 = Node("n5", [n3, n4])
        tm = SCons.Taskmaster.Taskmaster([n5])

        assert not tm.is_blocked()
        
        t1 = tm.next_task()
        assert t1.get_target() == n1
        assert not tm.is_blocked()
        
        t2 = tm.next_task()
        assert t2.get_target() == n2
        assert not tm.is_blocked()

        t4 = tm.next_task()
        assert t4.get_target() == n4
        assert tm.is_blocked()
        t4.executed()
        assert tm.is_blocked()
        
        t1.executed()
        assert tm.is_blocked()
        t2.executed()
        assert not tm.is_blocked()
        t3 = tm.next_task()
        assert t3.get_target() == n3
        assert tm.is_blocked()

        t3.executed()
        assert not tm.is_blocked()
        t5 = tm.next_task()
        assert t5.get_target() == n5
        assert not tm.is_blocked()

        assert tm.next_task() == None

        
        n4 = Node("n4")
        n4.set_state(SCons.Node.executed)
        tm = SCons.Taskmaster.Taskmaster([n4])
        assert tm.next_task() == None

        n1 = Node("n1")
        n2 = Node("n2", [n1])
        tm = SCons.Taskmaster.Taskmaster([n2,n2])
        t = tm.next_task()
        assert tm.is_blocked()
        t.executed()
        assert not tm.is_blocked()
        t = tm.next_task()
        assert tm.next_task() == None


        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1], [n2])
        tm = SCons.Taskmaster.Taskmaster([n3])
        t = tm.next_task()
        assert t.get_target() == n1
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n2
        t.executed()
        t = tm.next_task()
        assert t.get_target() == n3
        t.executed()
        assert tm.next_task() == None
    
    def test_cycle_detection(self):
        n1 = Node("n1")
        n2 = Node("n2", [n1])
        n3 = Node("n3", [n2])
        n1.kids = [n3]
        n3.parents.append(n1)

        try:
            tm = SCons.Taskmaster.Taskmaster([n3])
            t = tm.next_task()
        except SCons.Errors.UserError, e:
            assert str(e) == "Dependency cycle: n3 -> n1 -> n2 -> n3"
        else:
            assert 0
        
    def test_is_blocked(self):
        """Test whether a task is blocked

	Both default and overridden in a subclass.
	"""
	tm = SCons.Taskmaster.Taskmaster()
	assert not tm.is_blocked()

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def is_blocked(self):
	        return 1
	tm = MyTM()
	assert tm.is_blocked() == 1

    def test_stop(self):
        """Test the stop() method

        Both default and overridden in a subclass.
        """
        global built

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        
        tm = SCons.Taskmaster.Taskmaster([n3])
        t = tm.next_task()
        t.execute()
        assert built == "n1 built"
        t.executed()

        tm.stop()
        assert tm.next_task() is None

        class MyTM(SCons.Taskmaster.Taskmaster):
            def stop(self):
                global built
                built = "MyTM.stop()"
                SCons.Taskmaster.Taskmaster.stop(self)

        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1, n2])

        built = None
        tm = MyTM([n3])
        tm.next_task().execute()
        assert built == "n1 built"

        tm.stop()
        assert built == "MyTM.stop()"
        assert tm.next_task() is None

    def test_add_ready(self):
        """Test adding a task to the ready queue"""
        class MyTask:
            def __init__(self, tm, tlist, top):
                pass
            def make_ready(self):
                pass
        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1], tasker = MyTask)
        task = MyTask(tm, [], 0)
        tm.add_ready(task)
        assert tm.ready == [ task ], tm.ready

    def test_pending_to_ready(self):
        pass
    
    def test_pending_remove(self):
        pass



if __name__ == "__main__":
    suite = unittest.makeSuite(TaskmasterTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
