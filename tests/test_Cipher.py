import unittest

from openerm.Cipher import Cipher


class CipherTest(unittest.TestCase):

	def test_cipher_with_random_data(self):
		"""Verificar todos los algoritmos de cifrado con información random
		"""
		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		random_text = rnd_generator(size=200).encode("utf-8")

		c = Cipher()
		for t in c.available_types:
			with self.subTest(i=t[0]):
				c.type = t[0]
				tmp = c.encode(random_text)
				tmp = c.decode(tmp)
				self.assertEqual(random_text, tmp, "{0} != {1}".format(random_text, tmp))
