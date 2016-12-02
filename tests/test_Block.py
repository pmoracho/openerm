import unittest

from openerm.Block import Block


class BlockTest(unittest.TestCase):

	def test_dump_a_block(self):
		"""Verifica el "dump" de un bloque
		"""
		b = Block(default_compress_method=1, default_compress_level=1, default_encription_method=0)
		data = b.dump(tipo_bloque=2, data=b"Esto hace las veces de una pagina de reporte", variable_data=None)
		must_be = b'\x00\x00\x00<\x02\x01\x00\x00\x00\x001x\x9cs-.\xc9W\xc8HLNU\xc8I,V(KMN-VHIU(\xcdKT(HL\xcf\x04R@^QjA~QI*\x00]\x1f\x0f\xca'
		self.assertEqual(data, must_be, "{0} != {1}".format(data, must_be))
