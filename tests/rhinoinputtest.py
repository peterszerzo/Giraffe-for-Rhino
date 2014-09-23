import sys
import os

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import rhinoinput as ri


import unittest

class Test(unittest.TestCase):

	def test_number_only(self):

		inp = ri.RhinoInput("2")
		self.assertEqual(inp.get_no(), 2)

	def test_number_only_with_whitespace(self):

		inp = ri.RhinoInput(" 2  ")
		self.assertEqual(inp.get_no(), 2)

	def test_number_and_property(self):

		inp = ri.RhinoInput(" 2  [ncs 5]")
		self.assertEqual(inp.get_no(), 2)
		self.assertEqual(inp.get_prop(), "ncs 5")
		self.assertEqual(inp.get_name(), "")

	def test_number_and_name(self):

		inp = ri.RhinoInput(" 2  { some beam}")
		self.assertEqual(inp.get_no(), 2)
		self.assertEqual(inp.get_prop(), "")
		self.assertEqual(inp.get_name(), "some beam")

	def test_all(self):

		inp = ri.RhinoInput(" 2  [ gdiv 4  ] { some beam}")
		self.assertEqual(inp.get_no(), 2)
		self.assertEqual(inp.get_prop(), "gdiv 4")
		self.assertEqual(inp.get_name(), "some beam")


if __name__ == '__main__':

	unittest.main()