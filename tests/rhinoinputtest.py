# base imports
import sys
import os
import unittest

# import tested module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import rhinoinput as ri

class BaseTest(unittest.TestCase):

	def test_get_before(self):

		inp = ri.RhinoInput("adf [alma]")
		self.assertEqual(inp.get_before("[", "]"), "adf ")

	def test_get_between(self):

		inp = ri.RhinoInput("adf [alma]")
		self.assertEqual(inp.get_between("[", "]"), "alma")

	def test_does_not_have_a_number(self):

		inp = ri.RhinoInput("4alma")
		self.assertEqual(inp.has_number(), False)

	def test_has_number(self):

		inp = ri.RhinoInput("4")
		self.assertEqual(inp.has_number(), True)


class IntegrationTest(unittest.TestCase):

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

	def test_without_square_brackets(self):

		inp = ri.RhinoInput("gdiv 4 { some beam}")
		self.assertEqual(inp.get_no(), -1)
		self.assertEqual(inp.get_prop(), "gdiv 4")
		self.assertEqual(inp.get_name(), "some beam")


if __name__ == '__main__':

	unittest.main()