from openerm.OermClient import OermClient
from OermTestFixtures import OermTestFixtures


class OermClientTest(OermTestFixtures):

	# def test_catalogs(self):
	# 	"""Verifica la lista de catalogos
	# 	"""

	# 	# lista = {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True},
	# 	#			"catalogo2": {"name": "Ejemplo catalogo SQL", "type": "sql", "enabled": False}
	# 	# }

	# 	c = OermClient(self._configfile)
	# 	# print(c.catalogs())
	# 	self.assertEqual(c.catalogs(), {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True}})

	def test_catalogs(self):
		"""Verifica la lista de catalogos disponibles coincida con la que se acaba de salvar"""
		c = OermClient(self._configfile)
		self.assertEqual(c.catalogs(enabled=None), self.catalog_config)

	# def test_repos(self):
	# 	"""Verifica la lista de repositorios
	# 	"""
		# c.open_catalog("catalogo1")

	# 	c = OermClient(self._configfile)
	# 	c.open_catalog("catalogo1")
	# 	self.assertEqual(c.catalogs(), {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True}})
