__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import unittest

import SCons.Node



built_it = None

class Builder:
    def execute(self, **kw):
	global built_it
	built_it = 1

class Environment:
    def Dictionary(self, *args):
	pass



class NodeTestCase(unittest.TestCase):

    def test_build(self):
	"""Test building a node
	"""
	node = SCons.Node.Node()
	node.builder_set(Builder())
	node.env_set(Environment())
	node.path = "xxx"	# XXX FAKE SUBCLASS ATTRIBUTE
	node.sources = "yyy"	# XXX FAKE SUBCLASS ATTRIBUTE
	node.build()
	assert built_it

    def test_builder_set(self):
	"""Test setting a Node's Builder
	"""
	node = SCons.Node.Node()
	b = Builder()
	node.builder_set(b)
	assert node.builder == b

    def test_env_set(self):
	"""Test setting a Node's Environment
	"""
	node = SCons.Node.Node()
	e = Environment()
	node.env_set(e)
	assert node.env == e

    def test_has_signature(self):
	"""Test whether or not a node has a signature
	"""
	node = SCons.Node.Node()
	assert not node.has_signature()
	node.set_signature('xxx')
	assert node.has_signature()

    def test_set_signature(self):
	"""Test setting a Node's signature
	"""
	node = SCons.Node.Node()
	node.set_signature('yyy')
        assert node.signature == 'yyy'

    def test_get_signature(self):
	"""Test fetching a Node's signature
	"""
	node = SCons.Node.Node()
	node.set_signature('zzz')
        assert node.get_signature() == 'zzz'

    def test_add_dependency(self):
	"""Test adding dependencies to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.depends == []
	try:
	    node.add_dependency('zero')
	except TypeError:
	    pass
	node.add_dependency(['one'])
	assert node.depends == ['one']
	node.add_dependency(['two', 'three'])
	assert node.depends == ['one', 'two', 'three']

    def test_add_source(self):
	"""Test adding sources to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.sources == []
	try:
	    node.add_source('zero')
	except TypeError:
	    pass
	node.add_source(['one'])
	assert node.sources == ['one']
	node.add_source(['two', 'three'])
	assert node.sources == ['one', 'two', 'three']



if __name__ == "__main__":
    suite = unittest.makeSuite(NodeTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
