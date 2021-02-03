import unittest

from openerm.Utils import str_to_list
from openerm.Utils import AutoNum


class UtilsTest(unittest.TestCase):

	def test_str_to_list(self):
		"""Verifica str_to_list con varios ejemplos contra sus respectivos hashes
		"""
		tests = [
					("1-11, 65-89, 900-1500", -7067537569491430398),
					("1-33000", 8782425863038202611),
					("23", 3430009387528)
				]
		for t in tests:
			lista = str_to_list(t[0], 32000)
			self.assertEqual(hash(tuple(lista)), t[1], "\n\n[{0}] no coincide con su hash {1}".format(t[0], t[1]))

	def test_autonum_class(self):
		"""Verifica la clase Autonum
		"""

		def checkEqual(l1, l2):
			return len(l1) == len(l2) and sorted(l1) == sorted(l2)

		my_ids = AutoNum()
		my_ids.get("Prueba")
		self.assertEqual(my_ids.get("Prueba"), 1)
		self.assertEqual(my_ids.get("Otra cosa"), 2)
		self.assertTrue(checkEqual(my_ids.list(), [('Prueba', 1), ('Otra cosa', 2)]))
