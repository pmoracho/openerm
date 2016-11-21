import unittest

from openerm.Utils import *

class UtilsTest(unittest.TestCase):
	
	def test_str_to_list(self):
		"""Verifica str_to_list con varios ejemplos contra sus respectivos hashes
		"""
		tests = [ 
					("1-11, 65-89, 900-1500", -1514384382),
					("1-33000", -2003275021)
				]
		for t in tests:
			lista = str_to_list(t[0], 32000)
			self.assertEqual(hash(tuple(lista)), t[1], "\n\n[{0}] no coincide con su hash {1}".format(t[0], t[1]))
